# AI orchestrator log: real02

Model `Qwen/Qwen3.8-27B-FP8` @ `017b9c7af6b5689d5dd426a76e0bc077eb5ca20a`; started 2026-10-09T21:06:20Z, finished 2026-10-09T23:35:37Z; 948 events, 233 model calls.
Stopped in round 3: time budget: the final stages need the time left before the deadline - 20 min.

## Round 1

| seq | critic | of | status | counts | note |
|---|---|---|---|---|---|
| 1 | code | plausibility | ok | {"critical": 0, "major": 84, "minor": 56} |  |
| 2 | code | exterior | ok | {"critical": 1, "major": 4, "minor": 2} |  |
| 3 | code | views | ok | {"critical": 0, "major": 0, "minor": 0} |  |
| 4 | vision | r_L-1_salon | ok | {"kept": 0, "dropped": 0} |  |
| 5 | vision | r_L-1_salon_2 | ok | {"kept": 0, "dropped": 6} |  |
| 6 | vision | r_L-1_mutfak | ok | {"kept": 1, "dropped": 0} |  |
| 7 | vision | r_L-1_mutfak_2 | ok | {"kept": 4, "dropped": 0} |  |
| 8 | vision | r_L-1_koridor | ok | {"kept": 2, "dropped": 0} |  |
| 9 | vision | r_L-1_koridor_2 | ok | {"kept": 1, "dropped": 2} |  |
| 10 | vision | r_L-1_banyo | ok | {"kept": 2, "dropped": 0} |  |
| 11 | vision | r_L-1_banyo_2 | ok | {"kept": 0, "dropped": 2} |  |
| 12 | vision | r_L-1b_acik_mutfak | ok | {"kept": 3, "dropped": 6} |  |
| 13 | vision | r_L-1b_acik_mutfak_2 | ok | {"kept": 12, "dropped": 0} |  |
| 14 | vision | r_L-1b_oda | ok | {"kept": 0, "dropped": 3} |  |
| 15 | vision | r_L-1b_oda_2 | ok | {"kept": 0, "dropped": 3} |  |
| 16 | vision | r_L-1b_koridor | ok | {"kept": 0, "dropped": 1} |  |
| 17 | vision | r_L-1b_koridor_2 | ok | {"kept": 1, "dropped": 2} |  |
| 18 | vision | r_L-1b_banyo | ok | {"kept": 2, "dropped": 0} |  |
| 19 | vision | r_L-1b_banyo_2 | ok | {"kept": 2, "dropped": 0} |  |
| 20 | vision | r_L0_yatak_odasi | ok | {"kept": 0, "dropped": 3} |  |
| 21 | vision | r_L0_e_yatak_odasi | ok | {"kept": 3, "dropped": 0} |  |
| 22 | vision | r_L0_e_yatak_odasi_2 | ok | {"kept": 0, "dropped": 4} |  |
| 23 | vision | r_L0_yatak_odasi_2 | ok | {"kept": 0, "dropped": 4} |  |
| 24 | vision | r_L0_koridor | ok | {"kept": 1, "dropped": 2} |  |
| 25 | vision | r_L0_e_banyo | ok | {"kept": 3, "dropped": 0} |  |
| 26 | vision | r_L0_e_banyo_2 | ok | {"kept": 0, "dropped": 2} |  |
| 27 | vision | r_L0_koridor_2 | ok | {"kept": 2, "dropped": 2} |  |
| 28 | vision | r_L0_yatak_odasi_3 | ok | {"kept": 0, "dropped": 5} |  |
| 29 | vision | r_L0_yatak_odasi_4 | ok | {"kept": 1, "dropped": 2} |  |
| 30 | vision | r_L0_merdiven | ok | {"kept": 0, "dropped": 0} |  |
| 31 | vision | r_L0_merdiven_2 | ok | {"kept": 0, "dropped": 0} |  |
| 32 | vision | r_L0_banyo | ok | {"kept": 0, "dropped": 0} |  |
| 33 | vision | r_L0_banyo_2 | ok | {"kept": 0, "dropped": 2} |  |
| 34 | vision | r_L1_teras | ok | {"kept": 0, "dropped": 0} |  |
| 35 | vision | r_L1_oyun_aktivite_ve_dinlenme_odasi | ok | {"kept": 3, "dropped": 1} |  |
| 36 | vision | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | ok | {"kept": 2, "dropped": 0} |  |
| 37 | vision | r_L1_koridor | ok | {"kept": 1, "dropped": 2} |  |
| 38 | vision | r_L1_koridor_2 | ok | {"kept": 1, "dropped": 1} |  |
| 39 | vision | r_L1_banyo | ok | {"kept": 0, "dropped": 0} |  |
| 40 | vision | r_L1_banyo_2 | ok | {"kept": 2, "dropped": 0} |  |
| 41 | vision | ext_1 | ok | {"kept": 0, "dropped": 0} |  |
| 42 | vision | ext_2 | ok | {"kept": 0, "dropped": 0} |  |
| 43 | vision | ext_3 | ok | {"kept": 0, "dropped": 0} |  |
| 44 | vision | ext_4 | ok | {"kept": 0, "dropped": 0} |  |
| 45 | vision | ext_5 | ok | {"kept": 0, "dropped": 0} |  |
| 46 | vision | ext_6 | ok | {"kept": 1, "dropped": 0} |  |
| 312 | code | plausibility | ok | {"critical": 0, "major": 88, "minor": 56} |  |
| 313 | code | exterior | ok | {"critical": 1, "major": 4, "minor": 2} |  |
| 314 | code | views | ok | {"critical": 0, "major": 0, "minor": 0} |  |
| 315 | vision | r_L-1_salon | ok | {"kept": 3, "dropped": 0} |  |
| 316 | vision | r_L-1_salon_2 | ok | {"kept": 1, "dropped": 5} |  |
| 317 | vision | r_L-1_mutfak | ok | {"kept": 1, "dropped": 0} |  |
| 318 | vision | r_L-1_mutfak_2 | ok | {"kept": 4, "dropped": 0} |  |
| 319 | vision | r_L-1_koridor | ok | {"kept": 2, "dropped": 0} |  |
| 320 | vision | r_L-1_koridor_2 | ok | {"kept": 1, "dropped": 0} |  |
| 321 | vision | r_L-1_banyo | ok | {"kept": 2, "dropped": 0} |  |
| 322 | vision | r_L-1_banyo_2 | ok | {"kept": 0, "dropped": 2} |  |
| 323 | vision | r_L-1b_acik_mutfak | ok | {"kept": 1, "dropped": 7} |  |
| 324 | vision | r_L-1b_acik_mutfak_2 | ok | {"kept": 7, "dropped": 0} |  |
| 325 | vision | r_L-1b_oda | ok | {"kept": 1, "dropped": 2} |  |
| 326 | vision | r_L-1b_oda_2 | ok | {"kept": 0, "dropped": 3} |  |
| 327 | vision | r_L-1b_koridor | ok | {"kept": 1, "dropped": 1} |  |
| 328 | vision | r_L-1b_koridor_2 | ok | {"kept": 2, "dropped": 0} |  |
| 329 | vision | r_L-1b_banyo | ok | {"kept": 2, "dropped": 0} |  |
| 330 | vision | r_L-1b_banyo_2 | ok | {"kept": 3, "dropped": 0} |  |
| 331 | vision | r_L0_yatak_odasi | ok | {"kept": 0, "dropped": 3} |  |
| 332 | vision | r_L0_e_yatak_odasi | ok | {"kept": 1, "dropped": 4} |  |
| 333 | vision | r_L0_e_yatak_odasi_2 | ok | {"kept": 0, "dropped": 4} |  |
| 334 | vision | r_L0_yatak_odasi_2 | ok | {"kept": 1, "dropped": 3} |  |
| 335 | vision | r_L0_koridor | ok | {"kept": 2, "dropped": 0} |  |
| 336 | vision | r_L0_e_banyo | ok | {"kept": 2, "dropped": 0} |  |
| 337 | vision | r_L0_e_banyo_2 | ok | {"kept": 0, "dropped": 2} |  |
| 338 | vision | r_L0_koridor_2 | ok | {"kept": 0, "dropped": 0} |  |
| 339 | vision | r_L0_yatak_odasi_3 | ok | {"kept": 0, "dropped": 3} |  |
| 340 | vision | r_L0_yatak_odasi_4 | ok | {"kept": 1, "dropped": 2} |  |
| 341 | vision | r_L0_merdiven | ok | {"kept": 0, "dropped": 0} |  |
| 342 | vision | r_L0_merdiven_2 | ok | {"kept": 2, "dropped": 0} |  |
| 343 | vision | r_L0_banyo | ok | {"kept": 2, "dropped": 0} |  |
| 344 | vision | r_L0_banyo_2 | ok | {"kept": 0, "dropped": 2} |  |
| 345 | vision | r_L1_teras | ok | {"kept": 0, "dropped": 0} |  |
| 346 | vision | r_L1_oyun_aktivite_ve_dinlenme_odasi | ok | {"kept": 1, "dropped": 1} |  |
| 347 | vision | r_L1_oyun_aktivite_ve_dinlenme_odasi_2 | ok | {"kept": 2, "dropped": 0} |  |
| 348 | vision | r_L1_koridor | ok | {"kept": 1, "dropped": 2} |  |
| 349 | vision | r_L1_koridor_2 | ok | {"kept": 1, "dropped": 1} |  |
| 350 | vision | r_L1_banyo | ok | {"kept": 1, "dropped": 1} |  |
| 351 | vision | r_L1_banyo_2 | ok | {"kept": 1, "dropped": 0} |  |
| 352 | vision | ext_1 | ok | {"kept": 1, "dropped": 0} |  |
| 353 | vision | ext_2 | ok | {"kept": 1, "dropped": 0} |  |
| 354 | vision | ext_3 | ok | {"kept": 1, "dropped": 0} |  |
| 355 | vision | ext_4 | ok | {"kept": 1, "dropped": 0} |  |
| 356 | vision | ext_5 | ok | {"kept": 1, "dropped": 0} |  |
| 357 | vision | ext_6 | ok | {"kept": 1, "dropped": 0} |  |

Findings: 506 (103 dropped).

| seq | source | check | severity | target | finding | dropped |
|---|---|---|---|---|---|---|
| 47 | code | F1 | minor | f_L-1_024 | wardrobe is not a piece of a living room |  |
| 48 | code | F3 | major | f_L-1_053 | sofa_corner: its back is not on a wall (1.10 m off) |  |
| 49 | code | F4 | major | f_L-1_049 | armchair does not face its group (f_L-1_053, f_L-1_061) |  |
| 50 | code | F4 | major | f_L-1_053 | sofa_corner does not face its group (f_L-1_089, f_L-1_073) |  |
| 51 | code | F4 | major | f_L-1_089 | tv_unit stands behind the back of f_L-1_090, f_L-1_049, looking at it |  |
| 52 | code | F4 | major | f_L-1_090 | armchair does not face its group (f_L-1_061, f_L-1_053) |  |
| 53 | code | F5 | minor | f_L-1_061 | sofa without a coffee table |  |
| 54 | code | F6 | major | f_L-1_049 | armchair: the free zone in front of it is reaches out of the room |  |
| 55 | code | F6 | major | f_L-1_053 | no 0.9 m walkway from o_L-1_001 to win_L-1_001 (blocked by f_L-1_053) |  |
| 56 | code | F7 | major | f_L-1_059 | floor_lamp (1.60 m) stands in front of window win_L-1_001 (sill 0.90 m) |  |
| 57 | code | F7 | major | f_L-1_063 | floor_lamp (1.60 m) stands in front of window win_L-1_001 (sill 0.90 m) |  |
| 58 | code | F8 | major | f_L-1_073 | table_coffee stands alone in the room (no wall, no sofa / sofa_corner / armchair within 1.5 m) |  |
| 59 | code | F9 | major | f_L-1_021 | an unexplained drawn box (3.33 m², type unknown) is built |  |
| 60 | code | F9 | major | f_L-1_024 | wardrobe reaches 0.05 m² through the room outline |  |
| 61 | code | F9 | minor | f_L-1_060 | an unexplained drawn box (0.62 m², type unknown) is built |  |
| 62 | code | F9 | minor | f_L-1_070 | an unexplained drawn box (0.37 m², type unknown) is built |  |
| 63 | code | F9 | minor | f_L-1_071 | an unexplained drawn box (0.37 m², type unknown) is built |  |
| 64 | code | F9 | minor | f_L-1_087 | an unexplained drawn box (0.29 m², type unknown) is built |  |
| 65 | code | F1 | minor | f_L-1_023 | wardrobe is not a piece of a living room |  |
| 66 | code | F3 | major | f_L-1_054 | sofa_corner: its back is not on a wall (1.10 m off) |  |
| 67 | code | F3 | major | f_L-1_062 | sofa: its back is not on a wall (2.39 m off) |  |
| 68 | code | F4 | major | f_L-1_050 | armchair does not face its group (f_L-1_054, f_L-1_062) |  |
| 69 | code | F4 | major | f_L-1_054 | sofa_corner does not face its group (f_L-1_100, f_L-1_074) |  |
| 70 | code | F4 | major | f_L-1_062 | sofa does not face its group (f_L-1_100, f_L-1_074) |  |
| 71 | code | F4 | major | f_L-1_100 | tv_unit stands behind the back of f_L-1_101, f_L-1_050, looking at it |  |
| 72 | code | F4 | major | f_L-1_101 | armchair does not face its group (f_L-1_062, f_L-1_054) |  |
| 73 | code | F5 | minor | f_L-1_062 | sofa without a coffee table |  |
| 74 | code | F6 | major | f_L-1_050 | armchair: the free zone in front of it is reaches out of the room |  |
| 75 | code | F6 | major | f_L-1_054 | no 0.9 m walkway from o_L-1_002 to win_L-1_002 (blocked by f_L-1_054) |  |
| 76 | code | F7 | major | f_L-1_057 | floor_lamp (1.60 m) stands in front of window win_L-1_002 (sill 0.90 m) |  |
| 77 | code | F7 | major | f_L-1_065 | floor_lamp (1.60 m) stands in front of window win_L-1_002 (sill 0.90 m) |  |
| 78 | code | F8 | major | f_L-1_074 | table_coffee stands alone in the room (no wall, no sofa / sofa_corner / armchair within 1.5 m) |  |
| 79 | code | F9 | major | f_L-1_022 | an unexplained drawn box (3.33 m², type unknown) is built |  |
| 80 | code | F9 | major | f_L-1_023 | wardrobe reaches 0.05 m² through the room outline |  |
| 81 | code | F9 | minor | f_L-1_058 | an unexplained drawn box (0.62 m², type unknown) is built |  |
| 82 | code | F9 | minor | f_L-1_069 | an unexplained drawn box (0.37 m², type unknown) is built |  |
| 83 | code | F9 | minor | f_L-1_072 | an unexplained drawn box (0.37 m², type unknown) is built |  |
| 84 | code | F9 | minor | f_L-1_088 | an unexplained drawn box (0.29 m², type unknown) is built |  |
| 85 | code | F3 | major | f_L-1_008 | stove: its back is not on a wall (0.06 m off) |  |
| 86 | code | F5 | minor | f_L-1_093 | dining table with 2 of 6 chairs |  |
| 87 | code | F7 | major | f_L-1_067 | fridge (1.80 m) stands in front of window win_L-1_003 (sill 0.90 m) |  |
| 88 | code | F9 | minor | f_L-1_006 | an unexplained drawn box (0.10 m², type unknown) is built |  |
| 89 | code | F9 | minor | f_L-1_007 | an unexplained drawn box (0.10 m², type unknown) is built |  |
| 90 | code | F9 | major | f_L-1_008 | stove f_L-1_008 overlaps kitchen_counter f_L-1_002 by 0.41 m² |  |
| 91 | code | F9 | major | f_L-1_067 | fridge f_L-1_067 overlaps kitchen_counter f_L-1_003 by 0.39 m² |  |
| 92 | code | R3 | minor | d_L-1_003 | door d_L-1_003 swings into f_L-1_001 on one hinge side; the other hinge side is free |  |
| 93 | code | F3 | major | f_L-1_017 | stove: its back is not on a wall (0.06 m off) |  |
| 94 | code | F5 | minor | f_L-1_104 | dining table with 2 of 6 chairs |  |
| 95 | code | F7 | major | f_L-1_068 | fridge (1.80 m) stands in front of window win_L-1_004 (sill 0.90 m) |  |
| 96 | code | F9 | minor | f_L-1_015 | an unexplained drawn box (0.10 m², type unknown) is built |  |
| 97 | code | F9 | minor | f_L-1_016 | an unexplained drawn box (0.10 m², type unknown) is built |  |
| 98 | code | F9 | major | f_L-1_017 | stove f_L-1_017 overlaps kitchen_counter f_L-1_011 by 0.41 m² |  |
| 99 | code | F9 | major | f_L-1_068 | fridge f_L-1_068 overlaps kitchen_counter f_L-1_012 by 0.39 m² |  |
| 100 | code | R3 | minor | d_L-1_004 | door d_L-1_004 swings into f_L-1_010 on one hinge side; the other hinge side is free |  |
| 101 | code | F3 | major | f_L-1_056 | bathtub: its back is not on a wall (0.09 m off) |  |
| 102 | code | F4 | major | f_L-1_056 | bathtub faces a wall 0.00 m in front of it |  |
| 103 | code | R3 | minor | d_L-1_001 | door d_L-1_001 swings into f_L-1_026 on one hinge side; the other hinge side is free |  |
| 104 | code | R3 | minor | d_L-1_002 | door d_L-1_002 swings into f_L-1_025 on one hinge side; the other hinge side is free |  |
| 105 | code | F9 | major | f_L-1b_013 | stove f_L-1b_013 overlaps kitchen_counter f_L-1b_009 by 0.41 m² |  |
| 106 | code | F9 | major | f_L-1b_044 | an unexplained drawn box (1.34 m², type unknown) is built |  |
| 107 | code | F9 | minor | f_L-1b_047 | an unexplained drawn box (0.35 m², type unknown) is built |  |
| 108 | code | F9 | minor | f_L-1b_048 | an unexplained drawn box (0.62 m², type unknown) is built |  |
| 109 | code | F9 | minor | f_L-1b_049 | an unexplained drawn box (0.65 m², type unknown) is built |  |
| 110 | code | F9 | minor | f_L-1b_050 | an unexplained drawn box (0.65 m², type unknown) is built |  |
| 111 | code | F9 | major | f_L-1b_054 | fridge f_L-1b_054 overlaps kitchen_counter f_L-1b_010 by 0.39 m² |  |
| 112 | code | F9 | minor | f_L-1b_056 | an unexplained drawn box (0.16 m², type unknown) is built |  |
| 113 | code | F9 | major | f_L-1b_007 | stove f_L-1b_007 overlaps kitchen_counter f_L-1b_003 by 0.41 m² |  |
| 114 | code | F9 | minor | f_L-1b_045 | an unexplained drawn box (0.35 m², type unknown) is built |  |
| 115 | code | F9 | minor | f_L-1b_046 | an unexplained drawn box (0.62 m², type unknown) is built |  |
| 116 | code | F9 | minor | f_L-1b_051 | an unexplained drawn box (0.65 m², type unknown) is built |  |
| 117 | code | F9 | minor | f_L-1b_052 | an unexplained drawn box (0.65 m², type unknown) is built |  |
| 118 | code | F9 | major | f_L-1b_053 | fridge f_L-1b_053 overlaps kitchen_counter f_L-1b_004 by 0.39 m² |  |
| 119 | code | F9 | minor | f_L-1b_055 | an unexplained drawn box (0.16 m², type unknown) is built |  |
| 120 | code | F4 | major | f_L-1b_064 | chair faces a wall 0.11 m in front of it |  |
| 121 | code | F5 | minor | f_L-1b_061 | desk without a chair |  |
| 122 | code | F5 | minor | f_L-1b_065 | dining table with 1 of 4 chairs |  |
| 123 | code | F8 | major | f_L-1b_063 | armchair stands alone in the room (no wall, no sofa / sofa_corner / armchair within 2.0 m) |  |
| 124 | code | F4 | major | f_L-1b_069 | chair faces a wall 0.11 m in front of it |  |
| 125 | code | F5 | minor | f_L-1b_066 | desk without a chair |  |
| 126 | code | F5 | minor | f_L-1b_070 | dining table with 1 of 4 chairs |  |
| 127 | code | F8 | major | f_L-1b_068 | armchair stands alone in the room (no wall, no sofa / sofa_corner / armchair within 2.0 m) |  |
| 128 | code | F3 | major | f_L-1b_038 | toilet: its back is not on a wall (0.02 m off) |  |
| 129 | code | F3 | major | f_L-1b_042 | bathtub: its back is not on a wall (0.09 m off) |  |
| 130 | code | F4 | major | f_L-1b_042 | bathtub faces a wall 0.00 m in front of it |  |
| 131 | code | R3 | minor | d_L-1b_002 | door d_L-1b_002 swings into f_L-1b_036 on one hinge side; the other hinge side is free |  |
| 132 | code | F3 | major | f_L-1b_037 | toilet: its back is not on a wall (0.02 m off) |  |
| 133 | code | R3 | minor | d_L-1b_003 | door d_L-1b_003 swings into f_L-1b_035 on one hinge side; the other hinge side is free |  |
| 134 | code | F4 | major | f_L0_041 | bench faces a wall 0.04 m in front of it |  |
| 135 | code | F6 | major | f_L0_007 | no 0.9 m walkway from d_L0_001 to d_L0_002 (blocked by f_L0_007) |  |
| 136 | code | F6 | major | f_L0_007 | no 0.9 m walkway from d_L0_001 to win_L0_002 (blocked by f_L0_007) |  |
| 137 | code | F6 | major | f_L0_007 | no 0.9 m walkway from d_L0_002 to win_L0_002 (blocked by f_L0_007) |  |
| 138 | code | F9 | major | f_L0_031 | floor_lamp f_L0_031 overlaps bed_double f_L0_007 by 0.17 m² |  |
| 139 | code | F9 | major | f_L0_032 | floor_lamp f_L0_032 overlaps bed_double f_L0_007 by 0.22 m² |  |
| 140 | code | F6 | major | f_L0_008 | no 0.9 m walkway from d_L0_003 to d_L0_004 (blocked by f_L0_008) |  |
| 141 | code | F6 | major | f_L0_008 | no 0.9 m walkway from d_L0_003 to win_L0_003 (blocked by f_L0_008) |  |
| 142 | code | F6 | major | f_L0_008 | no 0.9 m walkway from d_L0_004 to win_L0_003 (blocked by f_L0_008) |  |
| 143 | code | F9 | major | f_L0_033 | floor_lamp f_L0_033 overlaps bed_double f_L0_008 by 0.17 m² |  |
| 144 | code | F9 | major | f_L0_034 | floor_lamp f_L0_034 overlaps bed_double f_L0_008 by 0.22 m² |  |
| 145 | code | F4 | major | f_L0_054 | bench faces a wall 0.04 m in front of it |  |
| 146 | code | F2 | major | f_L0_013 | shower 1.40 x 0.60 m is outside the type's product sizes |  |
| 147 | code | F3 | minor | f_L0_013 | shower: its back is not on a wall (0.07 m off) |  |
| 148 | code | F4 | major | f_L0_013 | shower faces a wall 0.10 m in front of it |  |
| 149 | code | F2 | major | f_L0_014 | shower 1.40 x 0.60 m is outside the type's product sizes |  |
| 150 | code | F3 | minor | f_L0_014 | shower: its back is not on a wall (0.07 m off) |  |
| 151 | code | F6 | major | f_L0_009 | wardrobe: the free zone in front of it is blocked by f_L0_029 |  |
| 152 | code | F6 | major | f_L0_011 | wardrobe: the free zone in front of it is blocked by f_L0_028 |  |
| 153 | code | F3 | major | f_L0_025 | bathtub: its back is not on a wall (0.09 m off) |  |
| 154 | code | F4 | major | f_L0_025 | bathtub faces a wall 0.00 m in front of it |  |
| 155 | code | R3 | minor | d_L0_007 | door d_L0_007 swings into f_L0_003 on one hinge side; the other hinge side is free |  |
| 156 | code | R3 | minor | d_L0_008 | door d_L0_008 swings into f_L0_005 on one hinge side; the other hinge side is free |  |
| 157 | code | F1 | minor | f_L1_009 | sofa is not a piece of a other room |  |
| 158 | code | F1 | minor | f_L1_012 | sofa is not a piece of a other room |  |
| 159 | code | F1 | minor | f_L1_027 | ottoman is not a piece of a other room |  |
| 160 | code | F3 | major | f_L1_009 | sofa: its back is not on a wall (2.48 m off) |  |
| 161 | code | F3 | major | f_L1_012 | sofa: its back is not on a wall (0.79 m off) |  |
| 162 | code | F4 | major | f_L1_029 | armchair does not face its group (f_L1_009, f_L1_012) |  |
| 163 | code | F8 | major | f_L1_030 | chair stands alone in the room (no wall, no table_dining / desk / kitchen_island within 0.8 m) |  |
| 164 | code | F9 | major | f_L1_005 | an unexplained drawn box (1.47 m², type unknown) is built |  |
| 165 | code | F9 | minor | f_L1_015 | an unexplained drawn box (0.71 m², type unknown) is built |  |
| 166 | code | F9 | major | f_L1_017 | an unexplained drawn box (2.48 m², type unknown) is built |  |
| 167 | code | F9 | minor | f_L1_024 | an unexplained drawn box (0.53 m², type unknown) is built |  |
| 168 | code | F9 | minor | f_L1_025 | an unexplained drawn box (0.53 m², type unknown) is built |  |
| 169 | code | F1 | minor | f_L1_010 | sofa is not a piece of a other room |  |
| 170 | code | F1 | minor | f_L1_011 | sofa is not a piece of a other room |  |
| 171 | code | F1 | minor | f_L1_028 | ottoman is not a piece of a other room |  |
| 172 | code | F3 | major | f_L1_010 | sofa: its back is not on a wall (2.48 m off) |  |
| 173 | code | F3 | major | f_L1_011 | sofa: its back is not on a wall (0.79 m off) |  |
| 174 | code | F4 | major | f_L1_033 | armchair does not face its group (f_L1_010, f_L1_011) |  |
| 175 | code | F8 | major | f_L1_034 | chair stands alone in the room (no wall, no table_dining / desk / kitchen_island within 0.8 m) |  |
| 176 | code | F9 | major | f_L1_006 | an unexplained drawn box (1.47 m², type unknown) is built |  |
| 177 | code | F9 | minor | f_L1_016 | an unexplained drawn box (0.71 m², type unknown) is built |  |
| 178 | code | F9 | major | f_L1_018 | an unexplained drawn box (2.48 m², type unknown) is built |  |
| 179 | code | F9 | minor | f_L1_023 | an unexplained drawn box (0.53 m², type unknown) is built |  |
| 180 | code | F9 | minor | f_L1_026 | an unexplained drawn box (0.53 m², type unknown) is built |  |
| 181 | code | F3 | major | f_L1_013 | toilet: its back is not on a wall (0.02 m off) |  |
| 182 | code | F3 | major | f_L1_019 | bathtub: its back is not on a wall (0.09 m off) |  |
| 183 | code | F4 | major | f_L1_019 | bathtub faces a wall 0.00 m in front of it |  |
| 184 | code | R3 | minor | d_L1_004 | door d_L1_004 swings into f_L1_007 on one hinge side; the other hinge side is free |  |
| 185 | code | F3 | major | f_L1_014 | toilet: its back is not on a wall (0.02 m off) |  |
| 186 | code | R3 | minor | d_L1_005 | door d_L1_005 swings into f_L1_008 on one hinge side; the other hinge side is free |  |
| 187 | code | X2 | minor | ro_001 | roof terrace ro_001 (r_L1_teras): the plan labels a terrace, the section r6 draws the roof closed over it; cut into the roof (brief roof_terraces: auto: the plan draws r_L1_teras as a room with a door to it (d_L1_003)) |  |
| 188 | code | X2 | minor | ro_002 | roof terrace ro_002 (r_L1_teras_2): the plan labels a terrace, the section r6 draws the roof closed over it; cut into the roof (brief roof_terraces: auto: the plan draws r_L1_teras_2 as a room with a door to it (d_L1_006)) |  |
| 189 | code | X2 | major | d_L1_004 | door height not drawn: its top 2.10 m above the floor would reach over the roof underside (1.10 m) at its wall; clipped 0.05 m under it (docs/milestone11.md §1.1 E8); still lower than a usable door (needs a dormer: review) |  |
| 190 | code | X2 | major | d_L1_005 | door height not drawn: its top 2.10 m above the floor would reach over the roof underside (1.10 m) at its wall; clipped 0.05 m under it (docs/milestone11.md §1.1 E8); still lower than a usable door (needs a dormer: review) |  |
| 191 | code | X2 | critical | dec_L1_011 | decor_dec_L1_011 pokes through the roof (top 5.35 m) |  |
| 192 | code | X3 | major | r_L0_yatak_odasi_3 | r_L0_yatak_odasi_3 (bedroom): 7.7 m of outer wall with no window or door: a blank facade |  |
| 193 | code | X3 | major | r_L0_yatak_odasi_4 | r_L0_yatak_odasi_4 (bedroom): 7.7 m of outer wall with no window or door: a blank facade |  |
| 194 | vision | F9 | major | f_L-1_092 | The tall cabinet (f_L-1_092) is rendered as a floating white box in the middle of the room, not attached to any wall or group. |  |
| 195 | vision | F9 | minor | f_L-1_018 | An unexplained drawn box (0.06 m², type unknown) is built. |  |
| 196 | vision | F9 | minor | f_L-1_082 | An unexplained drawn box (0.15 m², type unknown) is built. |  |
| 197 | vision | F9 | minor | f_L-1_084 | An unexplained drawn box (0.15 m², type unknown) is built. |  |
| 198 | vision | F9 | minor | f_L-1_086 | An unexplained drawn box (0.06 m², type unknown) is built. |  |
| 199 | vision | F1 | major | f_L-1_020 | A stair (f_L-1_020) is placed inside a corridor/hall room, which is an incorrect fixture type for this space. |  |
| 200 | vision | F9 | critical | f_L-1_020 | The stair (f_L-1_020) is represented as a giant box that covers the majority of the room's floor area, which is physically impossible and visually incorrect. |  |
| 201 | vision | F1 | major | f_L-1_019 | A large staircase is placed in the middle of the corridor, which is an incorrect fixture for a hallway of this size. |  |
| 202 | vision | F9 | major | f_L-1_056 | The bathtub is rendered as a solid green block in the plan and a white box in the 3D view, lacking the internal basin, drain, or faucet details visible in the source drawing. |  |
| 203 | vision | F9 | major | f_L-1_026 | The washbasin is rendered as a flat, empty rectangular depression in the countertop, missing the actual basin bowl and faucet shown in the source drawing. |  |
| 204 | vision | F9 | major | f_L-1b_002 | A large unexplained box (5.54x2.77 m) is built in the center of the room, which is not a standard furniture item and obstructs the space. |  |
| 205 | vision | F9 | minor | f_L-1b_058 | A small unexplained box (0.44x0.35 m) is built in the bottom right corner. |  |
| 206 | vision | F9 | minor | f_L-1b_060 | A small unexplained box (0.44x0.35 m) is built in the bottom right corner. |  |
| 207 | vision | F9 | major | f_L-1b_001 | A large 'unknown' piece (5.54x2.77 m) is built in the center of the room, which is not present in the source drawing and obstructs the main circulation space. |  |
| 208 | vision | F9 | major | f_L-1b_039 | A large 'kitchen_island' (0.9x2.13 m) is built in the center of the room, which is not present in the source drawing and obstructs the main circulation space. |  |
| 209 | vision | F9 | major | f_L-1b_043 | A 'kitchen_island' (1.64x0.82 m) is built in the upper-left area, which is not present in the source drawing. |  |
| 210 | vision | F9 | major | f_L-1b_005 | A 'kitchen_island' (1.59x0.6 m) is built in the right-center area, which is not present in the source drawing. |  |
| 211 | vision | F9 | major | f_L-1b_006 | An 'unknown' piece (0.62x0.6 m) is built in the upper-right corner, which is not present in the source drawing. |  |
| 212 | vision | F9 | major | f_L-1b_008 | An 'unknown' piece (0.51x0.11 m) is built in the upper-right corner, which is not present in the source drawing. |  |
| 213 | vision | F9 | major | f_L-1b_017 | A 'table_dining' (2.3x1.0 m) is built in the lower-right area, which is not present in the source drawing. |  |
| 214 | vision | F9 | major | f_L-1b_018 | A 'chair' is built in the lower-right area, which is not present in the source drawing. |  |
| 215 | vision | F9 | major | f_L-1b_019 | A 'chair' is built in the lower-right area, which is not present in the source drawing. |  |
| 216 | vision | F9 | major | f_L-1b_020 | A 'chair' is built in the lower-right area, which is not present in the source drawing. |  |
| 217 | vision | F9 | major | f_L-1b_021 | A 'chair' is built in the lower-right area, which is not present in the source drawing. |  |
| 218 | vision | F9 | major | f_L-1b_022 | A 'chair' is built in the lower-right area, which is not present in the source drawing. |  |
| 219 | vision | F1 | major | f_L-1b_015 | A stair is placed inside a corridor (hall) room, which is an incorrect fixture type for this space. |  |
| 220 | vision | F9 | critical | f_L-1b_042 | The bathtub (f_L-1b_042) is drawn as a giant box that extends significantly beyond the room's outer wall on the right side. |  |
| 221 | vision | F9 | major | f_L-1b_036 | The washbasin (f_L-1b_036) is drawn as a large block that overlaps the door swing area and extends into the wall on the left. |  |
| 222 | vision | F9 | major | f_L-1b_041 | The bathtub (f_L-1b_041) is drawn as a single continuous box that extends through the left wall of the room, which is physically impossible. |  |
| 223 | vision | F9 | major | f_L-1b_035 | The washbasin (f_L-1b_035) is drawn as a single continuous box that extends through the right wall of the room, which is physically impossible. |  |
| 224 | vision | F9 | major | f_L0_044 | The bench (f_L0_044) is floating in the middle of the room, not attached to any wall or furniture group. |  |
| 225 | vision | F9 | major | f_L0_042 | The nightstand (f_L0_042) is floating in the middle of the room, not attached to the bed or a wall. |  |
| 226 | vision | F9 | major | f_L0_043 | The nightstand (f_L0_043) is floating in the middle of the room, not attached to the bed or a wall. |  |
| 227 | vision | F1 | major | f_L0_036 | A shoe cabinet is placed in the hallway, which is an unusual fixture for this room type. |  |
| 228 | vision | F9 | major | f_L0_006 | The washbasin is rendered as a solid block with a recessed top, resembling a bathtub or a box, rather than a functional sink with a basin and faucet. |  |
| 229 | vision | F9 | major | f_L0_015 | The toilet is rendered as a simple rectangular box with a handle, completely missing the bowl, seat, and tank structure of a real toilet. |  |
| 230 | vision | F9 | major | f_L0_013 | The shower area is rendered as a flat green rectangle on the floor with no walls, glass, or fixtures, making it look like a rug or a floor marking rather than a shower. |  |
| 231 | vision | F1 | major | f_L0_037 | A console table is placed in a narrow corridor (hall), which is an inappropriate fixture for this room type. |  |
| 232 | vision | F1 | major | f_L0_038 | A shoe cabinet is placed in a narrow corridor (hall), which is an inappropriate fixture for this room type. |  |
| 233 | vision | F9 | minor | f_L0_057 | A bench is an unusual piece of furniture for a bedroom. |  |
| 234 | vision | F9 | major | f_L1_003 | The large green box (f_L1_003) is rendered as a solid, opaque block in the center of the room, blocking the view and floor space, rather than being a piece of furniture or a transparent element. |  |
| 235 | vision | F9 | major | f_L1_009 | The sofa (f_L1_009) is rendered as a solid, opaque block in the center of the room, blocking the view and floor space, rather than being a piece of furniture or a transparent element. |  |
| 236 | vision | F9 | major | f_L1_012 | The sofa (f_L1_012) is rendered as a solid, opaque block in the center of the room, blocking the view and floor space, rather than being a piece of furniture or a transparent element. |  |
| 237 | vision | F9 | major | f_L1_004 | An unexplained drawn box (13.56 m², type unknown) is built. |  |
| 238 | vision | F9 | minor | f_L1_033 | An unexplained drawn box (0.81 m², type unknown) is built. |  |
| 239 | vision | F1 | major | f_L1_002 | A full staircase is placed inside a 15.3 m2 corridor/hall, which is an incorrect fixture for this room type. |  |
| 240 | vision | F1 | major | f_L1_036 | A console table is placed in a corridor (hall). This is an unusual fixture for a circulation space and is likely an AI hallucination or misclassification of a wall element. |  |
| 241 | vision | F9 | critical | f_L1_020 | The bathtub (f_L1_020) is drawn as a giant box that extends far beyond the room's walls, covering a large portion of the plan and overlapping other areas. |  |
| 242 | vision | F9 | major | f_L1_008 | The washbasin (f_L1_008) is drawn as a box that is significantly larger than its specified dimensions (1.0x0.55 m), appearing oversized relative to the room and other fixtures. |  |
| 243 | vision | X6 | major | ext_6 | The camera is positioned at a direct frontal angle, showing only one facade. The checklist requires a 3/4 corner view that displays two facades of the building. |  |
| 244 | vision | F9 | major | f_L-1_022 | The piece f_L-1_022 is a large, unexplained box (3.33 m²) with no defined type, occupying a significant portion of the room. | duplicate of a code finding |
| 245 | vision | F9 | major | f_L-1_023 | The wardrobe f_L-1_023 is drawn extending through the room's boundary wall. | duplicate of a code finding |
| 246 | vision | F9 | minor | f_L-1_058 | The piece f_L-1_058 is an unexplained box (0.62 m²) with no defined type. | duplicate of a code finding |
| 247 | vision | F9 | minor | f_L-1_069 | The piece f_L-1_069 is an unexplained box (0.37 m²) with no defined type. | duplicate of a code finding |
| 248 | vision | F9 | minor | f_L-1_072 | The piece f_L-1_072 is an unexplained box (0.37 m²) with no defined type. | duplicate of a code finding |
| 249 | vision | F9 | minor | f_L-1_088 | The piece f_L-1_088 is an unexplained box (0.29 m²) with no defined type. | duplicate of a code finding |
| 250 | vision | F6 | critical | f_L-1_019 | The staircase blocks the main circulation path of the corridor, leaving no clear walkway. | code contradicts: F6 measured by code without a violation on f_L-1_019 |
| 251 | vision | F3 | major | f_L-1_099 | The console table is floating in the middle of the corridor instead of being placed against a wall. | code contradicts: F3 measured by code without a violation on f_L-1_099 |
| 252 | vision | F3 | major | f_L-1_052 | The toilet (f_L-1_052) is floating in the middle of the room. It is not attached to any wall, which is incorrect for a toilet installation. | code contradicts: F3 measured by code without a violation on f_L-1_052 |
| 253 | vision | F3 | major | f_L-1_025 | The washbasin (f_L-1_025) is floating in the middle of the room. It is not attached to any wall, which is incorrect for a washbasin installation. | code contradicts: F3 measured by code without a violation on f_L-1_025 |
| 254 | vision | F9 | major | f_L-1b_044 | A large unexplained box (0.82x1.64 m) is built in the upper right area, which is not a standard furniture item. | duplicate of a code finding |
| 255 | vision | F9 | minor | f_L-1b_047 | A small unexplained box (0.59x0.59 m) is built near the right wall. | duplicate of a code finding |
| 256 | vision | F9 | minor | f_L-1b_048 | A small unexplained box (0.79x0.79 m) is built in the bottom right corner. | duplicate of a code finding |
| 257 | vision | F9 | minor | f_L-1b_049 | A small unexplained box (0.82x0.79 m) is built in the bottom right area. | duplicate of a code finding |
| 258 | vision | F9 | minor | f_L-1b_050 | A small unexplained box (0.82x0.79 m) is built in the bottom right area. | duplicate of a code finding |
| 259 | vision | F9 | minor | f_L-1b_056 | A very small unexplained box (0.4x0.4 m) is built in the bottom right corner. | duplicate of a code finding |
| 260 | vision | F3 | major | f_L-1b_062 | The bookshelf is floating in the middle of the room, not placed against a wall as required for this type of furniture. | code contradicts: F3 measured by code without a violation on f_L-1b_062 |
| 261 | vision | F3 | major | f_L-1b_063 | The armchair is floating in the middle of the room, not placed against a wall or as part of a defined seating group. | code contradicts: F3 measured by code without a violation on f_L-1b_063 |
| 262 | vision | F3 | major | f_L-1b_065 | The dining table is floating in the middle of the room, not placed against a wall or in a corner. | code contradicts: F3 measured by code without a violation on f_L-1b_065 |
| 263 | vision | F3 | major | f_L-1b_066 | The desk is floating in the middle of the room and is not placed against a wall. | code contradicts: F3 measured by code without a violation on f_L-1b_066 |
| 264 | vision | F3 | major | f_L-1b_070 | The dining table is floating in the middle of the room and is not placed against a wall. | code contradicts: F3 measured by code without a violation on f_L-1b_070 |
| 265 | vision | F3 | major | f_L-1b_069 | The chair is floating in the middle of the room and is not placed against a wall. | code contradicts: F3 measured by code without a violation on f_L-1b_069 |
| 266 | vision | F8 | major | f_L-1b_016 | The stair (f_L-1b_016) is placed in the middle of the room, floating away from any walls, which is incorrect for a fixed architectural element. | code contradicts: F8 measured by code without a violation on f_L-1b_016 |
| 267 | vision | F8 | major | f_L-1b_015 | The stair is a floating piece in the middle of the room, not attached to any wall or part of a group. | code contradicts: F8 measured by code without a violation on f_L-1b_015 |
| 268 | vision | F3 | minor | f_L-1b_081 | The console table is placed in the middle of the corridor, not against a wall where it belongs. | code contradicts: F3 measured by code without a violation on f_L-1b_081 |
| 269 | vision | F6 | major | f_L0_010 | The clearance in front of the wardrobe is less than 0.6 m, making it difficult to open the doors and access the interior. | code contradicts: F6 measured by code without a violation on f_L0_010 |
| 270 | vision | F6 | major | f_L0_019 | The clearance beside the bed is less than 0.7 m, which is too narrow for comfortable access. | code contradicts: F6 measured by code without a violation on f_L0_019 |
| 271 | vision | F3 | major | f_L0_030 | The desk is not placed against a wall, which is unusual for this type of furniture and makes the room feel less organized. | code contradicts: F3 measured by code without a violation on f_L0_030 |
| 272 | vision | F3 | major | f_L0_008 | The bed (f_L0_008) is placed in the center of the room with its headboard facing the wall, but the foot of the bed is not facing free space; it is blocked by the nightstands and the window, violating the rule that the bed foot should face free space. | code contradicts: F3 measured by code without a violation on f_L0_008 |
| 273 | vision | F5 | major | f_L0_049 | The nightstand (f_L0_049) is not grouped with the bed (f_L0_008). It is placed far away from the bed, near the window, instead of being adjacent to the headboard or foot of the bed. | code contradicts: F5 measured by code without a violation on f_L0_049 |
| 274 | vision | F5 | major | f_L0_050 | The nightstand (f_L0_050) is not grouped with the bed (f_L0_008). It is placed far away from the bed, near the window, instead of being adjacent to the headboard or foot of the bed. | code contradicts: F5 measured by code without a violation on f_L0_050 |
| 275 | vision | F8 | major | f_L0_051 | The bench (f_L0_051) is floating in the room, away from any wall or group of furniture. It is not part of a coherent group like a bed or seating area. | code contradicts: F8 measured by code without a violation on f_L0_051 |
| 276 | vision | F6 | major | f_L0_020 | The bed is placed with less than 0.7m clearance on the left side, blocking the walkway to the door and wardrobe. | code contradicts: F6 measured by code without a violation on f_L0_020 |
| 277 | vision | F6 | major | f_L0_012 | The wardrobe is placed in a corner with no clearance in front of it, making it inaccessible. | code contradicts: F6 measured by code without a violation on f_L0_012 |
| 278 | vision | F3 | major | f_L0_027 | The desk is floating in the middle of the room, not against a wall. | code contradicts: F3 measured by code without a violation on f_L0_027 |
| 279 | vision | F5 | major | f_L0_020 | The nightstands are not placed next to the bed; one is by the window and the other is by the door. | code contradicts: F5 measured by code without a violation on f_L0_020 |
| 280 | vision | F3 | major | f_L0_035 | The console table is floating in the middle of the hallway instead of being placed against a wall. | code contradicts: F3 measured by code without a violation on f_L0_035 |
| 281 | vision | F6 | major | f_L0_036 | The shoe cabinet is placed directly in the main walkway of the hallway, obstructing the path. | code contradicts: F6 measured by code without a violation on f_L0_036 |
| 282 | vision | F3 | minor | f_L0_016 | The toilet is floating in the middle of the room, not placed against a wall. | code contradicts: F3 measured by code without a violation on f_L0_016 |
| 283 | vision | F3 | minor | f_L0_004 | The washbasin is floating in the middle of the room, not placed against a wall. | code contradicts: F3 measured by code without a violation on f_L0_004 |
| 284 | vision | F6 | major | f_L0_037 | The console table obstructs the walkway in the corridor, reducing the clear passage width below the required 0.9 m. | code contradicts: F6 measured by code without a violation on f_L0_037 |
| 285 | vision | F6 | major | f_L0_038 | The shoe cabinet obstructs the walkway in the corridor, reducing the clear passage width below the required 0.9 m. | code contradicts: F6 measured by code without a violation on f_L0_038 |
| 286 | vision | F3 | major | f_L0_021 | The bed is placed in the middle of the room with its headboard facing the wall, but the foot of the bed is not oriented towards free space as required; it is angled awkwardly relative to the room layout. | code contradicts: F3 measured by code without a violation on f_L0_021 |
| 287 | vision | F5 | major | f_L0_021 | The bed is not grouped with the nightstands. The nightstands are placed on the opposite wall, far from the bed, breaking the expected bed + nightstand group. | code contradicts: F5 measured by code without a violation on f_L0_021 |
| 288 | vision | F3 | major | f_L0_029 | The desk is floating in the middle of the room, not placed against a wall as required for a desk. | code contradicts: F3 measured by code without a violation on f_L0_029 |
| 289 | vision | F3 | major | f_L0_048 | The dresser is placed in the middle of the room, not against a wall as required for a dresser. | code contradicts: F3 measured by code without a violation on f_L0_048 |
| 290 | vision | F3 | major | f_L0_047 | The bench is placed in the middle of the room, not against a wall as required for a bench. | code contradicts: F3 measured by code without a violation on f_L0_047 |
| 291 | vision | F3 | major | f_L0_028 | The desk is floating in the middle of the room, not placed against a wall. | code contradicts: F3 measured by code without a violation on f_L0_028 |
| 292 | vision | F5 | major | f_L0_022 | The bed is not grouped with the nightstands; the nightstands are placed on the opposite wall (top) while the bed is in the center. | code contradicts: F5 measured by code without a violation on f_L0_022 |
| 293 | vision | F3 | major | f_L0_017 | The toilet (f_L0_017) is floating in the middle of the room, not placed against a wall. | code contradicts: F3 measured by code without a violation on f_L0_017 |
| 294 | vision | F3 | major | f_L0_005 | The washbasin (f_L0_005) is floating in the middle of the room, not placed against a wall. | code contradicts: F3 measured by code without a violation on f_L0_005 |
| 295 | vision | F9 | major | f_L1_017 | The large green box (f_L1_017) is rendered as a solid, opaque block in the center of the room, blocking the view and floor space, rather than being a piece of furniture or a transparent element. | duplicate of a code finding |
| 296 | vision | F6 | major | f_L1_002 | The staircase occupies the majority of the corridor's floor area, leaving no clear 0.9m walkway for circulation. | code contradicts: F6 measured by code without a violation on f_L1_002 |
| 297 | vision | F8 | minor | f_L1_032 | The console table is floating in the middle of the corridor without being part of a furniture group or against a wall. | code contradicts: F8 measured by code without a violation on f_L1_032 |
| 298 | vision | F8 | major | f_L1_036 | The console table is floating in the middle of the corridor, not attached to a wall or part of a furniture group. | code contradicts: F8 measured by code without a violation on f_L1_036 |
| 358 | code | F1 | minor | f_L-1_024 | wardrobe is not a piece of a living room |  |
| 359 | code | F3 | major | f_L-1_053 | sofa_corner: its back is not on a wall (1.10 m off) |  |
| 360 | code | F3 | major | f_L-1_091 | console_table: its back is not on a wall (0.76 m off) |  |
| 361 | code | F4 | major | f_L-1_049 | armchair does not face its group (f_L-1_053, f_L-1_061) |  |
| 362 | code | F4 | major | f_L-1_053 | sofa_corner does not face its group (f_L-1_089, f_L-1_073) |  |
| 363 | code | F4 | major | f_L-1_089 | tv_unit stands behind the back of f_L-1_090, f_L-1_049, looking at it |  |
| 364 | code | F4 | major | f_L-1_090 | armchair does not face its group (f_L-1_061, f_L-1_053) |  |
| 365 | code | F5 | minor | f_L-1_061 | sofa without a coffee table |  |
| 366 | code | F6 | major | f_L-1_049 | armchair: the free zone in front of it is reaches out of the room |  |
| 367 | code | F6 | major | f_L-1_053 | no 0.9 m walkway from o_L-1_001 to win_L-1_001 (blocked by f_L-1_053) |  |
| 368 | code | F7 | major | f_L-1_059 | floor_lamp (1.60 m) stands in front of window win_L-1_001 (sill 0.90 m) |  |
| 369 | code | F7 | major | f_L-1_063 | floor_lamp (1.60 m) stands in front of window win_L-1_001 (sill 0.90 m) |  |
| 370 | code | F8 | major | f_L-1_073 | table_coffee stands alone in the room (no wall, no sofa / sofa_corner / armchair within 1.5 m) |  |
| 371 | code | F9 | major | f_L-1_021 | an unexplained drawn box (3.33 m², type unknown) is built |  |
| 372 | code | F9 | major | f_L-1_024 | wardrobe reaches 0.05 m² through the room outline |  |
| 373 | code | F9 | minor | f_L-1_060 | an unexplained drawn box (0.62 m², type unknown) is built |  |
| 374 | code | F9 | minor | f_L-1_070 | an unexplained drawn box (0.37 m², type unknown) is built |  |
| 375 | code | F9 | minor | f_L-1_071 | an unexplained drawn box (0.37 m², type unknown) is built |  |
| 376 | code | F9 | minor | f_L-1_087 | an unexplained drawn box (0.29 m², type unknown) is built |  |
| 377 | code | F1 | minor | f_L-1_023 | wardrobe is not a piece of a living room |  |
| 378 | code | F3 | major | f_L-1_054 | sofa_corner: its back is not on a wall (1.10 m off) |  |
| 379 | code | F3 | major | f_L-1_062 | sofa: its back is not on a wall (2.39 m off) |  |
| 380 | code | F3 | major | f_L-1_104 | console_table: its back is not on a wall (0.76 m off) |  |
| 381 | code | F4 | major | f_L-1_050 | armchair does not face its group (f_L-1_054, f_L-1_062) |  |
| 382 | code | F4 | major | f_L-1_054 | sofa_corner does not face its group (f_L-1_102, f_L-1_074) |  |
| 383 | code | F4 | major | f_L-1_062 | sofa does not face its group (f_L-1_102, f_L-1_074) |  |
| 384 | code | F4 | major | f_L-1_102 | tv_unit stands behind the back of f_L-1_103, f_L-1_050, looking at it |  |
| 385 | code | F4 | major | f_L-1_103 | armchair does not face its group (f_L-1_062, f_L-1_054) |  |
| 386 | code | F5 | minor | f_L-1_062 | sofa without a coffee table |  |
| 387 | code | F6 | major | f_L-1_050 | armchair: the free zone in front of it is reaches out of the room |  |
| 388 | code | F6 | major | f_L-1_054 | no 0.9 m walkway from o_L-1_002 to win_L-1_002 (blocked by f_L-1_054) |  |
| 389 | code | F7 | major | f_L-1_057 | floor_lamp (1.60 m) stands in front of window win_L-1_002 (sill 0.90 m) |  |
| 390 | code | F7 | major | f_L-1_065 | floor_lamp (1.60 m) stands in front of window win_L-1_002 (sill 0.90 m) |  |
| 391 | code | F8 | major | f_L-1_074 | table_coffee stands alone in the room (no wall, no sofa / sofa_corner / armchair within 1.5 m) |  |
| 392 | code | F9 | major | f_L-1_022 | an unexplained drawn box (3.33 m², type unknown) is built |  |
| 393 | code | F9 | major | f_L-1_023 | wardrobe reaches 0.05 m² through the room outline |  |
| 394 | code | F9 | minor | f_L-1_058 | an unexplained drawn box (0.62 m², type unknown) is built |  |
| 395 | code | F9 | minor | f_L-1_069 | an unexplained drawn box (0.37 m², type unknown) is built |  |
| 396 | code | F9 | minor | f_L-1_072 | an unexplained drawn box (0.37 m², type unknown) is built |  |
| 397 | code | F9 | minor | f_L-1_088 | an unexplained drawn box (0.29 m², type unknown) is built |  |
| 398 | code | F3 | major | f_L-1_008 | stove: its back is not on a wall (0.06 m off) |  |
| 399 | code | F5 | minor | f_L-1_095 | dining table with 2 of 6 chairs |  |
| 400 | code | F7 | major | f_L-1_067 | fridge (1.80 m) stands in front of window win_L-1_003 (sill 0.90 m) |  |
| 401 | code | F9 | minor | f_L-1_006 | an unexplained drawn box (0.10 m², type unknown) is built |  |
| 402 | code | F9 | minor | f_L-1_007 | an unexplained drawn box (0.10 m², type unknown) is built |  |
| 403 | code | F9 | major | f_L-1_008 | stove f_L-1_008 overlaps kitchen_counter f_L-1_002 by 0.41 m² |  |
| 404 | code | F9 | major | f_L-1_067 | fridge f_L-1_067 overlaps kitchen_counter f_L-1_003 by 0.39 m² |  |
| 405 | code | R3 | minor | d_L-1_003 | door d_L-1_003 swings into f_L-1_001 on one hinge side; the other hinge side is free |  |
| 406 | code | F3 | major | f_L-1_017 | stove: its back is not on a wall (0.06 m off) |  |
| 407 | code | F5 | minor | f_L-1_107 | dining table with 2 of 6 chairs |  |
| 408 | code | F7 | major | f_L-1_068 | fridge (1.80 m) stands in front of window win_L-1_004 (sill 0.90 m) |  |
| 409 | code | F9 | minor | f_L-1_015 | an unexplained drawn box (0.10 m², type unknown) is built |  |
| 410 | code | F9 | minor | f_L-1_016 | an unexplained drawn box (0.10 m², type unknown) is built |  |
| 411 | code | F9 | major | f_L-1_017 | stove f_L-1_017 overlaps kitchen_counter f_L-1_011 by 0.41 m² |  |
| 412 | code | F9 | major | f_L-1_068 | fridge f_L-1_068 overlaps kitchen_counter f_L-1_012 by 0.39 m² |  |
| 413 | code | R3 | minor | d_L-1_004 | door d_L-1_004 swings into f_L-1_010 on one hinge side; the other hinge side is free |  |
| 414 | code | F3 | major | f_L-1_056 | bathtub: its back is not on a wall (0.09 m off) |  |
| 415 | code | F4 | major | f_L-1_056 | bathtub faces a wall 0.00 m in front of it |  |
| 416 | code | R3 | minor | d_L-1_001 | door d_L-1_001 swings into f_L-1_026 on one hinge side; the other hinge side is free |  |
| 417 | code | R3 | minor | d_L-1_002 | door d_L-1_002 swings into f_L-1_025 on one hinge side; the other hinge side is free |  |
| 418 | code | F9 | major | f_L-1b_013 | stove f_L-1b_013 overlaps kitchen_counter f_L-1b_009 by 0.41 m² |  |
| 419 | code | F9 | major | f_L-1b_040 | an unexplained drawn box (1.91 m², type unknown) is built |  |
| 420 | code | F9 | major | f_L-1b_044 | an unexplained drawn box (1.34 m², type unknown) is built |  |
| 421 | code | F9 | minor | f_L-1b_047 | an unexplained drawn box (0.35 m², type unknown) is built |  |
| 422 | code | F9 | minor | f_L-1b_048 | an unexplained drawn box (0.62 m², type unknown) is built |  |
| 423 | code | F9 | minor | f_L-1b_049 | an unexplained drawn box (0.65 m², type unknown) is built |  |
| 424 | code | F9 | minor | f_L-1b_050 | an unexplained drawn box (0.65 m², type unknown) is built |  |
| 425 | code | F9 | major | f_L-1b_054 | fridge f_L-1b_054 overlaps kitchen_counter f_L-1b_010 by 0.39 m² |  |
| 426 | code | F9 | minor | f_L-1b_056 | an unexplained drawn box (0.16 m², type unknown) is built |  |
| 427 | code | F9 | major | f_L-1b_007 | stove f_L-1b_007 overlaps kitchen_counter f_L-1b_003 by 0.41 m² |  |
| 428 | code | F9 | major | f_L-1b_043 | an unexplained drawn box (1.34 m², type unknown) is built |  |
| 429 | code | F9 | minor | f_L-1b_045 | an unexplained drawn box (0.35 m², type unknown) is built |  |
| 430 | code | F9 | minor | f_L-1b_046 | an unexplained drawn box (0.62 m², type unknown) is built |  |
| 431 | code | F9 | minor | f_L-1b_051 | an unexplained drawn box (0.65 m², type unknown) is built |  |
| 432 | code | F9 | minor | f_L-1b_052 | an unexplained drawn box (0.65 m², type unknown) is built |  |
| 433 | code | F9 | major | f_L-1b_053 | fridge f_L-1b_053 overlaps kitchen_counter f_L-1b_004 by 0.39 m² |  |
| 434 | code | F9 | minor | f_L-1b_055 | an unexplained drawn box (0.16 m², type unknown) is built |  |
| 435 | code | F4 | major | f_L-1b_064 | chair faces a wall 0.11 m in front of it |  |
| 436 | code | F5 | minor | f_L-1b_061 | desk without a chair |  |
| 437 | code | F5 | minor | f_L-1b_065 | dining table with 1 of 4 chairs |  |
| 438 | code | F8 | major | f_L-1b_063 | armchair stands alone in the room (no wall, no sofa / sofa_corner / armchair within 2.0 m) |  |
| 439 | code | F4 | major | f_L-1b_069 | chair faces a wall 0.11 m in front of it |  |
| 440 | code | F5 | minor | f_L-1b_066 | desk without a chair |  |
| 441 | code | F5 | minor | f_L-1b_070 | dining table with 1 of 4 chairs |  |
| 442 | code | F8 | major | f_L-1b_068 | armchair stands alone in the room (no wall, no sofa / sofa_corner / armchair within 2.0 m) |  |
| 443 | code | F3 | major | f_L-1b_038 | toilet: its back is not on a wall (0.02 m off) |  |
| 444 | code | F3 | major | f_L-1b_042 | bathtub: its back is not on a wall (0.09 m off) |  |
| 445 | code | F4 | major | f_L-1b_042 | bathtub faces a wall 0.00 m in front of it |  |
| 446 | code | R3 | minor | d_L-1b_002 | door d_L-1b_002 swings into f_L-1b_036 on one hinge side; the other hinge side is free |  |
| 447 | code | F3 | major | f_L-1b_037 | toilet: its back is not on a wall (0.02 m off) |  |
| 448 | code | R3 | minor | d_L-1b_003 | door d_L-1b_003 swings into f_L-1b_035 on one hinge side; the other hinge side is free |  |
| 449 | code | F4 | major | f_L0_041 | bench faces a wall 0.04 m in front of it |  |
| 450 | code | F6 | major | f_L0_007 | no 0.9 m walkway from d_L0_001 to d_L0_002 (blocked by f_L0_007) |  |
| 451 | code | F6 | major | f_L0_007 | no 0.9 m walkway from d_L0_001 to win_L0_002 (blocked by f_L0_007) |  |
| 452 | code | F6 | major | f_L0_007 | no 0.9 m walkway from d_L0_002 to win_L0_002 (blocked by f_L0_007) |  |
| 453 | code | F9 | major | f_L0_031 | floor_lamp f_L0_031 overlaps bed_double f_L0_007 by 0.17 m² |  |
| 454 | code | F9 | major | f_L0_032 | floor_lamp f_L0_032 overlaps bed_double f_L0_007 by 0.22 m² |  |
| 455 | code | F6 | major | f_L0_008 | no 0.9 m walkway from d_L0_003 to d_L0_004 (blocked by f_L0_008) |  |
| 456 | code | F6 | major | f_L0_008 | no 0.9 m walkway from d_L0_003 to win_L0_003 (blocked by f_L0_008) |  |
| 457 | code | F6 | major | f_L0_008 | no 0.9 m walkway from d_L0_004 to win_L0_003 (blocked by f_L0_008) |  |
| 458 | code | F9 | major | f_L0_033 | floor_lamp f_L0_033 overlaps bed_double f_L0_008 by 0.17 m² |  |
| 459 | code | F9 | major | f_L0_034 | floor_lamp f_L0_034 overlaps bed_double f_L0_008 by 0.22 m² |  |
| 460 | code | F4 | major | f_L0_053 | bench faces a wall 0.04 m in front of it |  |
| 461 | code | F2 | major | f_L0_013 | shower 1.40 x 0.60 m is outside the type's product sizes |  |
| 462 | code | F3 | minor | f_L0_013 | shower: its back is not on a wall (0.07 m off) |  |
| 463 | code | F4 | major | f_L0_013 | shower faces a wall 0.10 m in front of it |  |
| 464 | code | F2 | major | f_L0_014 | shower 1.40 x 0.60 m is outside the type's product sizes |  |
| 465 | code | F3 | minor | f_L0_014 | shower: its back is not on a wall (0.07 m off) |  |
| 466 | code | F6 | major | f_L0_009 | wardrobe: the free zone in front of it is blocked by f_L0_029 |  |
| 467 | code | F6 | major | f_L0_011 | wardrobe: the free zone in front of it is blocked by f_L0_028 |  |
| 468 | code | F3 | major | f_L0_025 | bathtub: its back is not on a wall (0.09 m off) |  |
| 469 | code | F4 | major | f_L0_025 | bathtub faces a wall 0.00 m in front of it |  |
| 470 | code | R3 | minor | d_L0_007 | door d_L0_007 swings into f_L0_003 on one hinge side; the other hinge side is free |  |
| 471 | code | R3 | minor | d_L0_008 | door d_L0_008 swings into f_L0_005 on one hinge side; the other hinge side is free |  |
| 472 | code | F1 | minor | f_L1_009 | sofa is not a piece of a other room |  |
| 473 | code | F1 | minor | f_L1_012 | sofa is not a piece of a other room |  |
| 474 | code | F1 | minor | f_L1_027 | ottoman is not a piece of a other room |  |
| 475 | code | F3 | major | f_L1_009 | sofa: its back is not on a wall (2.48 m off) |  |
| 476 | code | F3 | major | f_L1_012 | sofa: its back is not on a wall (0.79 m off) |  |
| 477 | code | F4 | major | f_L1_029 | armchair does not face its group (f_L1_009, f_L1_012) |  |
| 478 | code | F8 | major | f_L1_030 | chair stands alone in the room (no wall, no table_dining / desk / kitchen_island within 0.8 m) |  |
| 479 | code | F9 | major | f_L1_005 | an unexplained drawn box (1.47 m², type unknown) is built |  |
| 480 | code | F9 | minor | f_L1_015 | an unexplained drawn box (0.71 m², type unknown) is built |  |
| 481 | code | F9 | major | f_L1_017 | an unexplained drawn box (2.48 m², type unknown) is built |  |
| 482 | code | F9 | minor | f_L1_024 | an unexplained drawn box (0.53 m², type unknown) is built |  |
| 483 | code | F9 | minor | f_L1_025 | an unexplained drawn box (0.53 m², type unknown) is built |  |
| 484 | code | F1 | minor | f_L1_010 | sofa is not a piece of a other room |  |
| 485 | code | F1 | minor | f_L1_011 | sofa is not a piece of a other room |  |
| 486 | code | F1 | minor | f_L1_028 | ottoman is not a piece of a other room |  |
| 487 | code | F3 | major | f_L1_010 | sofa: its back is not on a wall (2.48 m off) |  |
| 488 | code | F3 | major | f_L1_011 | sofa: its back is not on a wall (0.79 m off) |  |
| 489 | code | F4 | major | f_L1_033 | armchair does not face its group (f_L1_010, f_L1_011) |  |
| 490 | code | F8 | major | f_L1_034 | chair stands alone in the room (no wall, no table_dining / desk / kitchen_island within 0.8 m) |  |
| 491 | code | F9 | major | f_L1_006 | an unexplained drawn box (1.47 m², type unknown) is built |  |
| 492 | code | F9 | minor | f_L1_016 | an unexplained drawn box (0.71 m², type unknown) is built |  |
| 493 | code | F9 | major | f_L1_018 | an unexplained drawn box (2.48 m², type unknown) is built |  |
| 494 | code | F9 | minor | f_L1_023 | an unexplained drawn box (0.53 m², type unknown) is built |  |
| 495 | code | F9 | minor | f_L1_026 | an unexplained drawn box (0.53 m², type unknown) is built |  |
| 496 | code | F3 | major | f_L1_013 | toilet: its back is not on a wall (0.02 m off) |  |
| 497 | code | F3 | major | f_L1_019 | bathtub: its back is not on a wall (0.09 m off) |  |
| 498 | code | F4 | major | f_L1_019 | bathtub faces a wall 0.00 m in front of it |  |
| 499 | code | R3 | minor | d_L1_004 | door d_L1_004 swings into f_L1_007 on one hinge side; the other hinge side is free |  |
| 500 | code | F3 | major | f_L1_014 | toilet: its back is not on a wall (0.02 m off) |  |
| 501 | code | R3 | minor | d_L1_005 | door d_L1_005 swings into f_L1_008 on one hinge side; the other hinge side is free |  |
| 502 | code | X2 | minor | ro_001 | roof terrace ro_001 (r_L1_teras): the plan labels a terrace, the section r6 draws the roof closed over it; cut into the roof (brief roof_terraces: auto: the plan draws r_L1_teras as a room with a door to it (d_L1_003)) |  |
| 503 | code | X2 | minor | ro_002 | roof terrace ro_002 (r_L1_teras_2): the plan labels a terrace, the section r6 draws the roof closed over it; cut into the roof (brief roof_terraces: auto: the plan draws r_L1_teras_2 as a room with a door to it (d_L1_006)) |  |
| 504 | code | X2 | major | d_L1_004 | door height not drawn: its top 2.10 m above the floor would reach over the roof underside (1.10 m) at its wall; clipped 0.05 m under it (docs/milestone11.md §1.1 E8); still lower than a usable door (needs a dormer: review) |  |
| 505 | code | X2 | major | d_L1_005 | door height not drawn: its top 2.10 m above the floor would reach over the roof underside (1.10 m) at its wall; clipped 0.05 m under it (docs/milestone11.md §1.1 E8); still lower than a usable door (needs a dormer: review) |  |
| 506 | code | X2 | critical | dec_L1_011 | decor_dec_L1_011 pokes through the roof (top 5.35 m) |  |
| 507 | code | X3 | major | r_L0_yatak_odasi_3 | r_L0_yatak_odasi_3 (bedroom): 7.7 m of outer wall with no window or door: a blank facade |  |
| 508 | code | X3 | major | r_L0_yatak_odasi_4 | r_L0_yatak_odasi_4 (bedroom): 7.7 m of outer wall with no window or door: a blank facade |  |
| 509 | vision | F9 | major | f_L-1_027 | The dining table is rendered as a massive, oversized slab that dominates the room, appearing disproportionately large compared to the chairs and the room dimensions. |  |
| 510 | vision | F9 | major | f_L-1_053 | The corner sofa is rendered as a solid, featureless beige block with no visible cushions, seams, or upholstery details, making it look like a piece of furniture model error. |  |
| 511 | vision | F9 | major | f_L-1_059 | The floor lamp is rendered with a strange, disjointed geometry where the lampshade appears to float or intersect awkwardly with the stand, and the base is obscured or malformed. |  |
| 512 | vision | F9 | major | f_L-1_054 | The sofa_corner is a giant box (4.38m x 1.97m) that occupies the center of the room, blocking the main walkway and appearing disproportionate to the space. |  |
| 513 | vision | F9 | major | f_L-1_094 | The tall cabinet (f_L-1_094) is rendered as a solid, featureless white block that looks like a placeholder or a rendering error, rather than a finished piece of furniture. |  |
| 514 | vision | F9 | minor | f_L-1_018 | An unexplained drawn box (0.06 m², type unknown) is built. |  |
| 515 | vision | F9 | minor | f_L-1_082 | An unexplained drawn box (0.15 m², type unknown) is built. |  |
| 516 | vision | F9 | minor | f_L-1_084 | An unexplained drawn box (0.15 m², type unknown) is built. |  |
| 517 | vision | F9 | minor | f_L-1_086 | An unexplained drawn box (0.06 m², type unknown) is built. |  |
| 518 | vision | F1 | major | f_L-1_020 | A stair (f_L-1_020) is placed inside a corridor/hall room, which is an incorrect fixture type for this space. |  |
| 519 | vision | F9 | critical | f_L-1_020 | The stair (f_L-1_020) is drawn as a giant box that covers the majority of the room's floor area, which is physically impossible and visually incorrect. |  |
| 520 | vision | F1 | major | f_L-1_101 | A console table is placed in a hallway (Koridor), which is an unusual furniture choice for this room type. |  |
| 521 | vision | F9 | major | f_L-1_056 | The bathtub is rendered as a simple open box (Image 3) without a drain, faucet, or internal basin, making it look like a storage bin rather than a functional fixture. |  |
| 522 | vision | F9 | major | f_L-1_026 | The washbasin is rendered as a flat, empty rectangular depression in the countertop (Images 2 & 3) with no visible bowl or basin depth, making it look like a cutout rather than a sink. |  |
| 523 | vision | F9 | major | f_L-1b_002 | A large unexplained box (5.54x2.77 m) is built in the middle of the room, which is not a standard furniture item and obstructs the space. |  |
| 524 | vision | F9 | major | f_L-1b_001 | A large unexplained box (5.54x2.77 m) is built in the center of the room, overlapping the kitchen island and bar stools. |  |
| 525 | vision | F9 | major | f_L-1b_039 | A large unexplained box (2.13x0.9 m) is built in the center of the room, overlapping the kitchen island and bar stools. |  |
| 526 | vision | F9 | major | f_L-1b_076 | A tall cabinet is built in the middle of the room, blocking the walkway between the kitchen island and the dining area. |  |
| 527 | vision | F9 | major | f_L-1b_077 | A bar stool is built in the middle of the room, not adjacent to a counter or island. |  |
| 528 | vision | F9 | major | f_L-1b_078 | A bar stool is built in the middle of the room, not adjacent to a counter or island. |  |
| 529 | vision | F9 | major | f_L-1b_079 | A bar stool is built in the middle of the room, not adjacent to a counter or island. |  |
| 530 | vision | F9 | major | f_L-1b_080 | A bar stool is built in the middle of the room, not adjacent to a counter or island. |  |
| 531 | vision | F4 | major | f_L-1b_061 | The desk is facing a wall instead of a window or open space, which is an incorrect orientation for a workspace. |  |
| 532 | vision | F1 | major | f_L-1b_075 | A console table is placed in a corridor (hall), which is an unusual fixture for this room type. |  |
| 533 | vision | F1 | major | f_L-1b_015 | A stair (f_L-1b_015) is placed inside a corridor/hall room, which is an incorrect fixture type for this space. |  |
| 534 | vision | F9 | critical | f_L-1b_015 | The stair piece (f_L-1b_015) is drawn as a large green box that extends through the room's boundary wall, which is a clear geometric error. |  |
| 535 | vision | F9 | major | f_L-1b_042 | The bathtub (f_L-1b_042) is placed in the corner of the room, but its front is facing directly into the wall with no clearance, making it unusable. |  |
| 536 | vision | F9 | major | f_L-1b_038 | The toilet (f_L-1b_038) is placed in the corner of the room, but its front is facing directly into the wall with no clearance, making it unusable. |  |
| 537 | vision | F9 | critical | f_L-1b_041 | The bathtub (f_L-1b_041) is drawn as a giant box that extends significantly beyond the room's outer wall on the left side. |  |
| 538 | vision | F9 | critical | f_L-1b_035 | The washbasin (f_L-1b_035) is drawn as a box that extends beyond the room's outer wall on the right side. |  |
| 539 | vision | F9 | major | f_L-1b_037 | The toilet (f_L-1b_037) is drawn as a box that extends beyond the room's outer wall on the bottom side. |  |
| 540 | vision | F4 | major | f_L0_007 | The bed's foot faces the wardrobe and the main walkway, blocking the primary circulation path in the room. |  |
| 541 | vision | F1 | minor | f_L0_053 | A bench is an unusual piece of furniture for a bedroom, especially placed at the foot of the bed. |  |
| 542 | vision | F1 | major | f_L0_035 | A console table is placed in a narrow corridor (hall), which is an inappropriate furniture type for this room type. |  |
| 543 | vision | F1 | major | f_L0_036 | A shoe cabinet is placed in a narrow corridor (hall), which is an inappropriate furniture type for this room type. |  |
| 544 | vision | F9 | major | f_L0_006 | The washbasin is rendered as a solid block with a recessed top surface, resembling a bathtub or a box, rather than a functional sink with a basin and faucet. |  |
| 545 | vision | F9 | major | f_L0_015 | The toilet is rendered as a simple rectangular box with a handle, completely missing the bowl, seat, and tank structure of a real toilet. |  |
| 546 | vision | F9 | minor | f_L0_056 | A bench is an unusual piece of furniture for a bedroom. |  |
| 547 | vision | F9 | critical | f_L0_002 | The stair piece (f_L0_002) is drawn as a single line with an arrow, which is a debug marker or a failed geometry representation, not a solid piece of furniture. |  |
| 548 | vision | F9 | major | o_L0_002 | The door opening (o_L0_002) is represented by a single orange line on the wall without a door leaf or swing arc, making it impossible to verify if the door opens correctly. |  |
| 549 | vision | F9 | major | f_L0_003 | The washbasin is rendered as a large, deep rectangular basin (resembling a small pool or trough) rather than a standard sink, which is a clear visual error in the model. |  |
| 550 | vision | F9 | major | f_L0_003 | The washbasin is rendered as a large, deep rectangular basin (resembling a small pool or trough) rather than a standard sink, which is a clear visual error in the model. |  |
| 551 | vision | F9 | major | f_L1_003 | The large box (f_L1_003) is rendered as a solid, opaque block in the middle of the room, which is not a plausible piece of furniture for a lounge area. |  |
| 552 | vision | F9 | major | f_L1_004 | An unexplained drawn box (13.56 m², type unknown) is built. |  |
| 553 | vision | F9 | minor | f_L1_033 | An unexplained drawn box (0.81 m², type unknown) is built. |  |
| 554 | vision | F1 | major | f_L1_002 | A full staircase is placed inside a 15.3 m2 corridor/hall, which is an inappropriate fixture for this room type. |  |
| 555 | vision | F1 | major | f_L1_036 | A console table is placed in a corridor (hall). This is an unusual fixture for a circulation space and is likely an AI hallucination or misclassification of a wall element. |  |
| 556 | vision | F4 | major | f_L1_007 | The washbasin is placed with its front facing the wall (90 degrees), making it unusable. It should face the open space of the room. |  |
| 557 | vision | F9 | major | f_L1_008 | The washbasin (f_L1_008) is placed in the middle of the room, floating away from any wall, which is unusual for a bathroom fixture. |  |
| 558 | vision | X3 | major | building | The main entrance door is not visible at grade on the front facade; the ground floor appears to have only windows and no clear entry point. |  |
| 559 | vision | X2 | critical | building | The building is described as having 4 levels, but the render only shows a single-story structure with a roof, missing the upper three floors. |  |
| 560 | vision | X2 | critical | building | A vertical element (likely a chimney or vent) is clearly poking through the roof surface. |  |
| 561 | vision | X3 | major | building | The main facade facing the camera is almost entirely blank, with only two doors and no visible windows, which is implausible for a multi-story building. |  |
| 562 | vision | X6 | major | ext_5 | The camera is positioned at a high angle looking down at the building, rather than at the required eye level (1.5-1.7 m). This results in a bird's-eye view where the roof dominates the composition and the vertical lines of the building appear to converge. |  |
| 563 | vision | X6 | major | ext_6 | The camera is positioned at a direct frontal angle, showing only one facade. The checklist requires a 3/4 corner view where two facades are visible. |  |
| 564 | vision | F9 | major | f_L-1_022 | A large unexplained box (3.33 m²) is built in the top-right corner, overlapping the room boundary and the window band. | duplicate of a code finding |
| 565 | vision | F9 | minor | f_L-1_058 | An unexplained box (0.62 m²) is built in the bottom-right corner, partially obscuring the window. | duplicate of a code finding |
| 566 | vision | F9 | minor | f_L-1_069 | An unexplained box (0.37 m²) is built in the bottom-left corner, partially obscuring the window. | duplicate of a code finding |
| 567 | vision | F9 | minor | f_L-1_072 | An unexplained box (0.37 m²) is built in the bottom-left corner, partially obscuring the window. | duplicate of a code finding |
| 568 | vision | F9 | minor | f_L-1_088 | An unexplained box (0.29 m²) is built in the top-right area, floating in the middle of the room. | duplicate of a code finding |
| 569 | vision | F3 | major | f_L-1_052 | The toilet (f_L-1_052) is floating in the middle of the room. It is not attached to any wall, which is incorrect for a standard toilet installation. | code contradicts: F3 measured by code without a violation on f_L-1_052 |
| 570 | vision | F3 | major | f_L-1_025 | The washbasin (f_L-1_025) is floating in the middle of the room. It is not attached to a wall, which is incorrect for a standard washbasin installation. | code contradicts: F3 measured by code without a violation on f_L-1_025 |
| 571 | vision | F9 | major | f_L-1b_040 | A large unexplained box (2.13x0.9 m) is built in the middle of the room, which is not a standard furniture item and obstructs the space. | duplicate of a code finding |
| 572 | vision | F9 | major | f_L-1b_044 | A large unexplained box (0.82x1.64 m) is built in the middle of the room, which is not a standard furniture item and obstructs the space. | duplicate of a code finding |
| 573 | vision | F9 | minor | f_L-1b_047 | A small unexplained box (0.59x0.59 m) is built in the middle of the room, which is not a standard furniture item. | duplicate of a code finding |
| 574 | vision | F9 | minor | f_L-1b_048 | A small unexplained box (0.79x0.79 m) is built in the middle of the room, which is not a standard furniture item. | duplicate of a code finding |
| 575 | vision | F9 | minor | f_L-1b_049 | A small unexplained box (0.82x0.79 m) is built in the middle of the room, which is not a standard furniture item. | duplicate of a code finding |
| 576 | vision | F9 | minor | f_L-1b_050 | A small unexplained box (0.82x0.79 m) is built in the middle of the room, which is not a standard furniture item. | duplicate of a code finding |
| 577 | vision | F9 | minor | f_L-1b_056 | A small unexplained box (0.4x0.4 m) is built in the middle of the room, which is not a standard furniture item. | duplicate of a code finding |
| 578 | vision | F3 | major | f_L-1b_062 | The bookshelf is floating in the middle of the room, not placed against a wall as required for this type of furniture. | code contradicts: F3 measured by code without a violation on f_L-1b_062 |
| 579 | vision | F3 | major | f_L-1b_065 | The dining table is floating in the middle of the room, not placed against a wall or in a defined dining area. | code contradicts: F3 measured by code without a violation on f_L-1b_065 |
| 580 | vision | F3 | major | f_L-1b_066 | The desk is floating in the middle of the room and is not placed against a wall. | code contradicts: F3 measured by code without a violation on f_L-1b_066 |
| 581 | vision | F3 | major | f_L-1b_067 | The bookshelf is floating in the middle of the room and is not placed against a wall. | code contradicts: F3 measured by code without a violation on f_L-1b_067 |
| 582 | vision | F3 | major | f_L-1b_070 | The dining table is floating in the middle of the room and is not placed against a wall. | code contradicts: F3 measured by code without a violation on f_L-1b_070 |
| 583 | vision | F3 | minor | f_L-1b_075 | The console table is not placed against a wall; it is floating in the middle of the corridor. | code contradicts: F3 measured by code without a violation on f_L-1b_075 |
| 584 | vision | F6 | major | f_L0_010 | The clearance in front of the wardrobe is less than 0.6 m, making it difficult to open the doors and access the interior. | code contradicts: F6 measured by code without a violation on f_L0_010 |
| 585 | vision | F6 | major | f_L0_019 | The clearance beside the bed is less than 0.7 m, which is too narrow for comfortable access. | code contradicts: F6 measured by code without a violation on f_L0_019 |
| 586 | vision | F3 | major | f_L0_030 | The desk is not placed against a wall, which is unusual for this type of furniture and makes the room feel less organized. | code contradicts: F3 measured by code without a violation on f_L0_030 |
| 587 | vision | F3 | major | f_L0_007 | The bed is placed with its headboard against the side wall (right wall) instead of the back wall, which is an unusual orientation for a bedroom layout. | code contradicts: F3 measured by code without a violation on f_L0_007 |
| 588 | vision | F5 | major | f_L0_042 | The nightstand (f_L0_042) is placed at the foot of the bed rather than beside the headboard, failing to form a proper bedside group. | code contradicts: F5 measured by code without a violation on f_L0_042 |
| 589 | vision | F5 | major | f_L0_043 | The nightstand (f_L0_043) is placed at the foot of the bed rather than beside the headboard, failing to form a proper bedside group. | code contradicts: F5 measured by code without a violation on f_L0_043 |
| 590 | vision | F8 | major | f_L0_044 | The bench (f_L0_044) is floating in the middle of the room, not attached to a wall or part of a furniture group. | code contradicts: F8 measured by code without a violation on f_L0_044 |
| 591 | vision | F3 | major | f_L0_008 | The bed is placed in the middle of the room with its headboard facing the open space, not against a wall. | code contradicts: F3 measured by code without a violation on f_L0_008 |
| 592 | vision | F5 | major | f_L0_048 | The nightstand is not grouped with the bed; it is located far away near the window. | code contradicts: F5 measured by code without a violation on f_L0_048 |
| 593 | vision | F5 | major | f_L0_049 | The nightstand is not grouped with the bed; it is located far away near the window. | code contradicts: F5 measured by code without a violation on f_L0_049 |
| 594 | vision | F8 | major | f_L0_050 | The bench is floating in the room without being part of a furniture group or against a wall. | code contradicts: F8 measured by code without a violation on f_L0_050 |
| 595 | vision | F6 | major | f_L0_020 | The bed is placed in the center of the room, blocking the main circulation path and leaving insufficient clearance (less than 0.9m) for a walkway on the left side. | code contradicts: F6 measured by code without a violation on f_L0_020 |
| 596 | vision | F5 | major | f_L0_020 | The bed is not grouped with the nightstands; the nightstands are placed at the foot of the bed rather than at the headboard, and one is missing. | code contradicts: F5 measured by code without a violation on f_L0_020 |
| 597 | vision | F3 | major | f_L0_027 | The desk is floating in the middle of the room and is not placed against a wall. | code contradicts: F3 measured by code without a violation on f_L0_027 |
| 598 | vision | F3 | minor | f_L0_016 | The toilet is floating in the middle of the room, not placed against a wall. | code contradicts: F3 measured by code without a violation on f_L0_016 |
| 599 | vision | F3 | minor | f_L0_004 | The washbasin is floating in the middle of the room, not placed against a wall. | code contradicts: F3 measured by code without a violation on f_L0_004 |
| 600 | vision | F3 | major | f_L0_021 | The bed is placed in the middle of the room with its headboard facing a wall, but the foot of the bed is not oriented towards free space as required; it is angled or positioned such that it does not align with the room's main circulation or wall layout. | code contradicts: F3 measured by code without a violation on f_L0_021 |
| 601 | vision | F5 | major | f_L0_021 | The nightstands (f_L0_045, f_L0_046) are not placed beside the bed (f_L0_021) to form a coherent group. They are located on the opposite wall, far from the bed's headboard. | code contradicts: F5 measured by code without a violation on f_L0_021 |
| 602 | vision | F8 | major | f_L0_047 | The bench (f_L0_047) is floating in the room without being part of a functional group (like a bed or seating area) and is not placed against a wall where it would be expected. | code contradicts: F8 measured by code without a violation on f_L0_047 |
| 603 | vision | F3 | major | f_L0_028 | The desk is floating in the middle of the room, not placed against a wall. | code contradicts: F3 measured by code without a violation on f_L0_028 |
| 604 | vision | F5 | major | f_L0_022 | The bed is not grouped with the nightstands; the nightstands are placed on the opposite wall. | code contradicts: F5 measured by code without a violation on f_L0_022 |
| 605 | vision | F3 | major | f_L0_026 | The bathtub is floating in the middle of the room, not placed against a wall. | code contradicts: F3 measured by code without a violation on f_L0_026 |
| 606 | vision | F3 | major | f_L0_017 | The toilet is floating in the middle of the room, not placed against a wall. | code contradicts: F3 measured by code without a violation on f_L0_017 |
| 607 | vision | F9 | major | f_L1_017 | The large box (f_L1_017) is rendered as a solid, opaque block in the middle of the room, which is not a plausible piece of furniture for a lounge area. | duplicate of a code finding |
| 608 | vision | F6 | major | f_L1_002 | The large staircase occupies the majority of the corridor's floor area, leaving no clear 0.9m walkway for circulation. | code contradicts: F6 measured by code without a violation on f_L1_002 |
| 609 | vision | F3 | minor | f_L1_032 | The console table is floating in the middle of the corridor without being placed against a wall or part of a furniture group. | code contradicts: F3 measured by code without a violation on f_L1_032 |
| 610 | vision | F3 | major | f_L1_001 | The stair (f_L1_001) is placed in the middle of the room area, not against a wall. Stairs are typically built-in structures or require specific wall support, and floating in the center of a corridor is architecturally incorrect. | code contradicts: F3 measured by code without a violation on f_L1_001 |
| 611 | vision | F6 | major | f_L1_013 | The toilet is placed in a corner with no clearance in front of it, blocking the walkway and making it impossible to use. | code contradicts: F6 measured by code without a violation on f_L1_013 |

Edits:

| seq | tool | args | accepted | failed checks | score | label | reason | re-run from | before | after |
|---|---|---|---|---|---|---|---|---|---|---|
| 299 | move_piece | {"piece_id": "f_L-1_053", "snap_wall_id": "w_L-1_007", "offset": 2.5, "reason": "Snap the corner sofa's back to the west wall to fix the 1.10 m off-wall and the | False | snap: f_L-1_053: no free place on wall w_L-1_007 (doors, windows, at most 0.3 m from the drawn place) | 0.0 -> 0.0 | adjusted_by_ai | Snap the corner sofa's back to the west wall to fix the 1.10 m off-wall and the blocked door-to-window walkway. |  | ![](images/r1_039_move_piece_before_r_L-1_salon.png) |  |
| 300 | move_piece | {"piece_id": "f_L-1_053", "center": [1.15, 3.27], "reason": "Shift the corner sofa west so its back sits on the west wall, clearing the door-to-window walkway." | False | drawn_lock: f_L-1_053: a drawn piece moves at most 0.3 m (this move: 1.93 m) | 0.0 -> 0.0 | adjusted_by_ai | Shift the corner sofa west so its back sits on the west wall, clearing the door-to-window walkway. |  | ![](images/r1_040_move_piece_before_r_L-1_salon.png) |  |
| 301 | move_piece | {"piece_id": "f_L-1_053", "center": [2.78, 3.27], "reason": "Nudge the corner sofa 0.30 m west toward the west wall to reduce the off-wall distance and open the | False | f_L-1_053: clearance_ok, f_L-1_061: clearance_ok, score: plausibility -38 -> -61 (F5 f_L-1_053: sofa_corner without a coffee table; F6 f_L-1_053: sofa_corner: the free zone in front of it is blocked by f_L-1_061; F6 f_L-1_061: sofa: the free zone in front of it is blocked by f_L-1_053) | 0.0 -> 0.0 | adjusted_by_ai | Nudge the corner sofa 0.30 m west toward the west wall to reduce the off-wall distance and open the door-to-window walkway. |  | ![](images/r1_041_move_piece_before_r_L-1_salon.png) |  |
| 302 | move_piece | {"piece_id": "f_L-1_059", "center": [1.28, 1.6], "reason": "Move the floor lamp away from the window so it no longer blocks the 0.90 m sill."} | False | drawn_lock: f_L-1_059: a drawn piece moves at most 0.3 m (this move: 0.90 m) | 0.0 -> 0.0 | adjusted_by_ai | Move the floor lamp away from the window so it no longer blocks the 0.90 m sill. |  | ![](images/r1_042_move_piece_before_r_L-1_salon.png) |  |
| 303 | move_piece | {"piece_id": "f_L-1_063", "center": [4.3, 1.6], "reason": "Move the floor lamp away from the window so it no longer blocks the 0.90 m sill."} | False | drawn_lock: f_L-1_063: a drawn piece moves at most 0.3 m (this move: 0.86 m) | 0.0 -> 0.0 | adjusted_by_ai | Move the floor lamp away from the window so it no longer blocks the 0.90 m sill. |  | ![](images/r1_043_move_piece_before_r_L-1_salon.png) |  |
| 304 | move_piece | {"piece_id": "f_L-1_059", "center": [1.28, 0.99], "reason": "Nudge the floor lamp 0.3 m away from the window to clear the 0.90 m sill."} | True |  | 0.0 -> 0.0 | adjusted_by_ai | Nudge the floor lamp 0.3 m away from the window to clear the 0.90 m sill. | refit | ![](images/r1_044_move_piece_before_r_L-1_salon.png) | ![](images/r1_045_move_piece_after_r_L-1_salon.png) |
| 305 | move_piece | {"piece_id": "f_L-1_063", "center": [4.3, 1.04], "reason": "Nudge the floor lamp 0.3 m away from the window to clear the 0.90 m sill."} | False | f_L-1_053: no_overlap | 0.0 -> 0.0 | adjusted_by_ai | Nudge the floor lamp 0.3 m away from the window to clear the 0.90 m sill. |  | ![](images/r1_046_move_piece_before_r_L-1_salon.png) |  |
| 306 | move_piece | {"piece_id": "f_L-1_063", "center": [4.6, 0.74], "reason": "Nudge the floor lamp 0.3 m east along the window to clear the 0.90 m sill zone."} | False | score: plausibility -28 -> -38 (F9 f_L-1_064: floor_lamp f_L-1_064 overlaps floor_lamp f_L-1_063 by 0.11 m²) | 0.0 -> 0.0 | adjusted_by_ai | Nudge the floor lamp 0.3 m east along the window to clear the 0.90 m sill zone. |  | ![](images/r1_047_move_piece_before_r_L-1_salon.png) |  |
| 612 | resize_piece | {"piece_id": "f_L-1b_041", "size": [1.7, 0.75], "reason": "Drawn bathtub box (1.83 m) extends past the left outer wall; resize to a real 1.70 m tub so it fits i | False | drawn_lock: f_L-1b_041: drawn fixed equipment keeps its drawn size | 87.0 -> 87.0 | adjusted_by_ai | Drawn bathtub box (1.83 m) extends past the left outer wall; resize to a real 1.70 m tub so it fits inside the room. |  | ![](images/r1_039_resize_piece_before_r_L-1b_banyo_2.png) |  |
| 613 | resize_piece | {"piece_id": "f_L-1b_035", "size": [0.6, 0.45], "reason": "Drawn washbasin box (1.0 m wide) extends past the right outer wall; resize to a real 0.60 m basin so  | False | drawn_lock: f_L-1b_035: drawn fixed equipment keeps its drawn size | 87.0 -> 87.0 | adjusted_by_ai | Drawn washbasin box (1.0 m wide) extends past the right outer wall; resize to a real 0.60 m basin so it fits inside the room. |  | ![](images/r1_040_resize_piece_before_r_L-1b_banyo_2.png) |  |
| 614 | move_piece | {"piece_id": "f_L-1b_037", "center": [9.1208, 10.215], "reason": "Snap the toilet's back edge onto the bottom wall (it was 0.02 m off) and pull it fully inside  | False | drawn_lock: f_L-1b_037: drawn fixed equipment (toilet) is never moved | 87.0 -> 87.0 | adjusted_by_ai | Snap the toilet's back edge onto the bottom wall (it was 0.02 m off) and pull it fully inside the room. |  | ![](images/r1_041_move_piece_before_r_L-1b_banyo_2.png) |  |
| 615 | move_piece | {"piece_id": "f_L-1b_041", "center": [8.6035, 10.884], "reason": "Shift the drawn bathtub right so its left edge sits on the room's left wall instead of extendi | False | drawn_lock: f_L-1b_041: drawn fixed equipment (bathtub) is never moved | 87.0 -> 87.0 | adjusted_by_ai | Shift the drawn bathtub right so its left edge sits on the room's left wall instead of extending beyond it. |  | ![](images/r1_042_move_piece_before_r_L-1b_banyo_2.png) |  |
| 616 | move_piece | {"piece_id": "f_L-1b_035", "center": [9.7048, 10.2104], "reason": "Shift the drawn washbasin left so its right edge sits on the room's right wall instead of ext | False | drawn_lock: f_L-1b_035: drawn fixed equipment (washbasin) is never moved | 87.0 -> 87.0 | adjusted_by_ai | Shift the drawn washbasin left so its right edge sits on the room's right wall instead of extending beyond it. |  | ![](images/r1_043_move_piece_before_r_L-1b_banyo_2.png) |  |
| 617 | remove_piece | {"piece_id": "f_L-1_020", "reason": "The 2.71x2.10 m 'stair' box covers ~47% of this 11.9 m² corridor and is not a real stair: the plan crop shows no treads or  | False | drawn_lock: f_L-1_020: drawn fixed equipment (stair) is never removed | 100.0 -> 100.0 | adjusted_by_ai | The 2.71x2.10 m 'stair' box covers ~47% of this 11.9 m² corridor and is not a real stair: the plan crop shows no treads or stair symbol in this area, the corridor label (7 m²) only matches once this box is excluded, and the actual stairs of the building are drawn in the central hall of the other flo |  | ![](images/r1_045_remove_piece_before_r_L-1_koridor.png) |  |
| 618 | resize_piece | {"piece_id": "f_L-1_020", "size": [1.2, 2.1], "reason": "The drawn 2.71 m wide stair box covers ~47% of the 11.9 m² corridor and is physically impossible; resiz | False | drawn_lock: f_L-1_020: drawn fixed equipment keeps its drawn size | 100.0 -> 100.0 | adjusted_by_ai | The drawn 2.71 m wide stair box covers ~47% of the 11.9 m² corridor and is physically impossible; resizing to a real 1.2 m wide straight stair keeps the drawn stair's position and 2.1 m run while making it a plausible fixture. |  | ![](images/r1_046_resize_piece_before_r_L-1_koridor.png) |  |
| 619 | remove_piece | {"piece_id": "f_L-1b_015", "reason": "The stair box (2.71×2.1 m, centre 9.11,8.64) extends ~0.44 m past the room's west boundary wall (x=7.787) and ~0.15 m past | False | drawn_lock: f_L-1b_015: drawn fixed equipment (stair) is never removed | 100.0 -> 100.0 | adjusted_by_ai | The stair box (2.71×2.1 m, centre 9.11,8.64) extends ~0.44 m past the room's west boundary wall (x=7.787) and ~0.15 m past the south edge (y=7.593), a clear drawing error; the plan crop shows the stair drawn in the central hall, not in this corridor, so this duplicate stair belongs to the other corr |  | ![](images/r1_048_remove_piece_before_r_L-1b_koridor_2.png) |  |
| 620 | resize_piece | {"piece_id": "f_L-1b_015", "size": [2.7141, 2.1], "reason": "No-op size check before moving the stair back inside the room boundary."} | False | drawn_lock: f_L-1b_015: drawn fixed equipment keeps its drawn size | 100.0 -> 100.0 | adjusted_by_ai | No-op size check before moving the stair back inside the room boundary. |  | ![](images/r1_049_resize_piece_before_r_L-1b_koridor_2.png) |  |
| 621 | move_piece | {"piece_id": "f_L-1b_015", "center": [9.1143, 8.6436], "reason": "No-op move to test whether the drawn stair's position can be adjusted at all."} | False | drawn_lock: f_L-1b_015: drawn fixed equipment (stair) is never moved | 100.0 -> 100.0 | adjusted_by_ai | No-op move to test whether the drawn stair's position can be adjusted at all. |  | ![](images/r1_050_move_piece_before_r_L-1b_koridor_2.png) |  |
| 622 | move_piece | {"piece_id": "f_L0_002", "center": [9.1143, 8.665], "reason": "Re-center the stair footprint inside the room so it no longer overhangs the south wall (front arr | False | drawn_lock: f_L0_002: drawn fixed equipment (stair) is never moved | 100.0 -> 100.0 | adjusted_by_ai | Re-center the stair footprint inside the room so it no longer overhangs the south wall (front arrow was pointing out of the room). |  | ![](images/r1_052_move_piece_before_r_L0_merdiven_2.png) |  |
| 623 | rotate_piece | {"piece_id": "f_L0_002", "front_deg": 90, "reason": "Turn the stair's front (direction of ascent) to face north, inside the room, instead of pointing out throug | False | frontless: f_L0_002: a stair has no front to turn | 100.0 -> 100.0 | adjusted_by_ai | Turn the stair's front (direction of ascent) to face north, inside the room, instead of pointing out through the south wall. |  | ![](images/r1_053_rotate_piece_before_r_L0_merdiven_2.png) |  |
| 624 | resize_piece | {"piece_id": "f_L0_002", "size": [2.1, 2.1], "reason": "Shrink the stair footprint to a real 2.1 m flight so it fits inside the 2.6 m deep room instead of overh | False | drawn_lock: f_L0_002: drawn fixed equipment keeps its drawn size | 100.0 -> 100.0 | adjusted_by_ai | Shrink the stair footprint to a real 2.1 m flight so it fits inside the 2.6 m deep room instead of overhanging the south wall. |  | ![](images/r1_054_resize_piece_before_r_L0_merdiven_2.png) |  |
| 625 | move_piece | {"piece_id": "f_L-1_053", "snap_wall_id": "w_L-1_007", "offset": 0, "reason": "Snap the corner sofa's back to the west wall to clear the door-to-window walkway  | False | snap: f_L-1_053: no free place on wall w_L-1_007 (doors, windows, at most 0.3 m from the drawn place) | 0.0 -> 0.0 | adjusted_by_ai | Snap the corner sofa's back to the west wall to clear the door-to-window walkway and fix the off-wall back. |  | ![](images/r1_056_move_piece_before_r_L-1_salon.png) |  |
| 626 | move_piece | {"piece_id": "f_L-1_091", "snap_wall_id": "w_L-1_007", "offset": 0, "reason": "Snap the console table's back onto the west wall to fix the 0.76 m off-wall back. | True |  | 0.0 -> 0.0 | added_by_ai | Snap the console table's back onto the west wall to fix the 0.76 m off-wall back. | refit | ![](images/r1_057_move_piece_before_r_L-1_salon.png) | ![](images/r1_058_move_piece_after_r_L-1_salon.png) |
| 627 | move_piece | {"piece_id": "f_L-1_053", "center": [2.3, 3.27], "reason": "Shift the corner sofa west so its back sits on the west wall and it no longer blocks the door-to-win | False | drawn_lock: f_L-1_053: a drawn piece moves at most 0.3 m (this move: 0.78 m) | 0.0 -> 0.0 | adjusted_by_ai | Shift the corner sofa west so its back sits on the west wall and it no longer blocks the door-to-window walkway. |  | ![](images/r1_059_move_piece_before_r_L-1_salon.png) |  |
| 628 | move_piece | {"piece_id": "f_L-1_053", "center": [2.78, 3.27], "reason": "Nudge the corner sofa 0.3 m west toward the west wall to reduce the off-wall back and clear the wal | False | f_L-1_053: clearance_ok, f_L-1_061: clearance_ok, score: plausibility -38 -> -61 (F5 f_L-1_053: sofa_corner without a coffee table; F6 f_L-1_053: sofa_corner: the free zone in front of it is blocked by f_L-1_061; F6 f_L-1_061: sofa: the free zone in front of it is blocked by f_L-1_053) | 0.0 -> 0.0 | adjusted_by_ai | Nudge the corner sofa 0.3 m west toward the west wall to reduce the off-wall back and clear the walkway. |  | ![](images/r1_060_move_piece_before_r_L-1_salon.png) |  |
| 629 | move_piece | {"piece_id": "f_L-1_053", "center": [3.08, 3.57], "reason": "Nudge the corner sofa 0.3 m north to open the door-to-window walkway that it currently blocks."} | False | max_tries: f_L-1_053 was edited 3 times in this round |  | adjusted_by_ai | Nudge the corner sofa 0.3 m north to open the door-to-window walkway that it currently blocks. |  |  |  |
| 630 | move_piece | {"piece_id": "f_L-1_059", "center": [1.28, 1.6], "reason": "Move the floor lamp away from the window so it no longer stands in front of win_L-1_001."} | False | drawn_lock: f_L-1_059: a drawn piece moves at most 0.3 m (this move: 0.90 m) | 0.0 -> 0.0 | adjusted_by_ai | Move the floor lamp away from the window so it no longer stands in front of win_L-1_001. |  | ![](images/r1_061_move_piece_before_r_L-1_salon.png) |  |
| 631 | move_piece | {"piece_id": "f_L-1_063", "center": [4.3, 1.6], "reason": "Move the floor lamp away from the window so it no longer stands in front of win_L-1_001."} | False | drawn_lock: f_L-1_063: a drawn piece moves at most 0.3 m (this move: 0.86 m) | 0.0 -> 0.0 | adjusted_by_ai | Move the floor lamp away from the window so it no longer stands in front of win_L-1_001. |  | ![](images/r1_062_move_piece_before_r_L-1_salon.png) |  |
| 632 | move_piece | {"piece_id": "f_L-1_059", "center": [1.28, 0.99], "reason": "Nudge the floor lamp 0.3 m north, the maximum allowed, to pull it off the window band."} | True |  | 0.0 -> 0.0 | adjusted_by_ai | Nudge the floor lamp 0.3 m north, the maximum allowed, to pull it off the window band. | refit | ![](images/r1_063_move_piece_before_r_L-1_salon.png) | ![](images/r1_064_move_piece_after_r_L-1_salon.png) |
| 633 | resize_piece | {"piece_id": "f_L-1_054", "size": [2.6, 0.95], "reason": "The drawn 4.38x1.97 m 'sofa_corner' is a misread oversized box; resize to a real corner-sofa footprint | False | product_size: f_L-1_054: 2.60 x 0.95 m is not a real sofa_corner size (size table) | 0.0 -> 0.0 | adjusted_by_ai | The drawn 4.38x1.97 m 'sofa_corner' is a misread oversized box; resize to a real corner-sofa footprint so it no longer blocks the walkway. |  | ![](images/r1_066_resize_piece_before_r_L-1_salon_2.png) |  |
| 634 | move_piece | {"piece_id": "f_L-1_054", "snap_wall_id": "w_L-1_015", "offset": 2, "reason": "Snap the corner sofa's back onto the right exterior wall to clear the door-to-win | False | snap: f_L-1_054: no free place on wall w_L-1_015 (doors, windows, at most 0.3 m from the drawn place) | 0.0 -> 0.0 | adjusted_by_ai | Snap the corner sofa's back onto the right exterior wall to clear the door-to-window walkway and satisfy the back-on-wall check. |  | ![](images/r1_067_move_piece_before_r_L-1_salon_2.png) |  |
| 635 | resize_piece | {"piece_id": "f_L-1_054", "size": [2.4481, 2.4301], "reason": "Resize the misread 4.38x1.97 m box to a real corner-sofa product size (Rivet Emerly 96in) so it f | False | f_L-1_054: no_overlap, f_L-1_062: doors_free, f_L-1_062: no_overlap, score: plausibility -68 -> -88 (F3 f_L-1_054: sofa_corner: its back is not on a wall (1.97 m off); F6 f_L-1_054: no 0.9 m walkway from o_L-1_002 to win_L-1_002 (blocked by f_L-1_054, f_L-1_062); F8 f_L-1_057: floor_lamp stands alon | 0.0 -> 0.0 | adjusted_by_ai | Resize the misread 4.38x1.97 m box to a real corner-sofa product size (Rivet Emerly 96in) so it fits the room and clears the walkway. |  | ![](images/r1_068_resize_piece_before_r_L-1_salon_2.png) |  |
| 636 | move_piece | {"piece_id": "f_L-1_054", "center": [13.7, 2.0], "reason": "Shift the corner sofa toward the right wall so its back sits on the exterior wall and it no longer b | False | max_tries: f_L-1_054 was edited 3 times in this round |  | adjusted_by_ai | Shift the corner sofa toward the right wall so its back sits on the exterior wall and it no longer blocks the door-to-window walkway. |  |  |  |
| 637 | move_piece | {"piece_id": "f_L-1_062", "snap_wall_id": "w_L-1_015", "offset": 1.5, "reason": "Snap the sofa's back onto the right exterior wall to fix the 2.39 m off-wall fi | False | snap: f_L-1_062: no free place on wall w_L-1_015 (doors, windows, at most 0.3 m from the drawn place) | 0.0 -> 0.0 | adjusted_by_ai | Snap the sofa's back onto the right exterior wall to fix the 2.39 m off-wall finding. |  | ![](images/r1_069_move_piece_before_r_L-1_salon_2.png) |  |
| 638 | move_piece | {"piece_id": "f_L-1_104", "snap_wall_id": "w_L-1_015", "offset": 3.5, "reason": "Snap the console table's back onto the right exterior wall to fix the 0.76 m of | True |  | 0.0 -> 0.0 | added_by_ai | Snap the console table's back onto the right exterior wall to fix the 0.76 m off-wall finding. | refit | ![](images/r1_070_move_piece_before_r_L-1_salon_2.png) | ![](images/r1_071_move_piece_after_r_L-1_salon_2.png) |
| 639 | remove_piece | {"piece_id": "f_L-1b_001", "reason": "5.54x2.77 m unexplained box in the room center is a misread drawing artifact (hatch/outline), not furniture; it overlaps t | False | no_change: f_L-1b_001 is not built already | 55.0 -> 55.0 | adjusted_by_ai | 5.54x2.77 m unexplained box in the room center is a misread drawing artifact (hatch/outline), not furniture; it overlaps the island and stools. |  | ![](images/r1_073_remove_piece_before_r_L-1b_acik_mutfak_2.png) |  |
| 640 | remove_piece | {"piece_id": "f_L-1b_039", "reason": "Duplicate second kitchen island (2.13x0.9 m) overlapping the real island f_L-1b_005 and the bar stools; the plan shows onl | False | drawn_lock: f_L-1b_039: drawn fixed equipment (kitchen_island) is never removed | 55.0 -> 55.0 | adjusted_by_ai | Duplicate second kitchen island (2.13x0.9 m) overlapping the real island f_L-1b_005 and the bar stools; the plan shows only one island. |  | ![](images/r1_074_remove_piece_before_r_L-1b_acik_mutfak_2.png) |  |
| 641 | change_type | {"piece_id": "f_L-1b_001", "type": "sofa", "reason": "The 5.54x2.77 m drawn box in the open-kitchen center is a sofa zone (open-plan living area); typing it as  | False | room_type: sofa is not a piece a kitchen room may hold here | 55.0 -> 55.0 | adjusted_by_ai | The 5.54x2.77 m drawn box in the open-kitchen center is a sofa zone (open-plan living area); typing it as sofa explains the footprint and stops it being an unexplained box. |  | ![](images/r1_075_change_type_before_r_L-1b_acik_mutfak_2.png) |  |
| 642 | change_type | {"piece_id": "f_L-1b_043", "type": "tall_cabinet", "reason": "The 0.82x1.64 m drawn box against the north wall is a tall cabinet (pantry) by footprint and posit | False | product_size: f_L-1b_043: 0.82 x 1.64 m does not fit a tall_cabinet (size table) | 55.0 -> 55.0 | adjusted_by_ai | The 0.82x1.64 m drawn box against the north wall is a tall cabinet (pantry) by footprint and position. |  | ![](images/r1_076_change_type_before_r_L-1b_acik_mutfak_2.png) |  |
| 643 | change_type | {"piece_id": "f_L-1b_001", "type": "table_dining", "reason": "The large 5.54x2.77 m drawn box in the open-kitchen center is a dining table zone; typing it as ta | False | product_size: f_L-1b_001: 5.54 x 2.77 m does not fit a table_dining (size table) | 55.0 -> 55.0 | adjusted_by_ai | The large 5.54x2.77 m drawn box in the open-kitchen center is a dining table zone; typing it as table_dining explains the footprint within the kitchen room type. |  | ![](images/r1_077_change_type_before_r_L-1b_acik_mutfak_2.png) |  |
| 644 | change_type | {"piece_id": "f_L-1b_043", "type": "wardrobe", "reason": "The 0.82x1.64 m drawn box against the north wall is a wardrobe/storage cabinet by footprint and positi | False | room_type: wardrobe is not a piece a kitchen room may hold here | 55.0 -> 55.0 | adjusted_by_ai | The 0.82x1.64 m drawn box against the north wall is a wardrobe/storage cabinet by footprint and position. |  | ![](images/r1_078_change_type_before_r_L-1b_acik_mutfak_2.png) |  |
| 645 | change_type | {"piece_id": "f_L-1b_043", "type": "display_cabinet", "reason": "The 0.82x1.64 m drawn box against the north wall is a display cabinet by footprint and position | False | room_type: display_cabinet is not a piece a kitchen room may hold here | 55.0 -> 55.0 | adjusted_by_ai | The 0.82x1.64 m drawn box against the north wall is a display cabinet by footprint and position. |  | ![](images/r1_079_change_type_before_r_L-1b_acik_mutfak_2.png) |  |
| 646 | move_piece | {"piece_id": "f_L-1b_076", "center": [8.0, 6.9], "reason": "Move the AI tall cabinet from the middle of the room to the north wall so it no longer blocks the wa | False | f_L-1b_076: inside_room, score: plausibility 55 -> 35 (F3 f_L-1b_076: tall_cabinet: its back is not on a wall (0.09 m off); F9 f_L-1b_076: tall_cabinet reaches 0.05 m² through the room outline) | 55.0 -> 35.0 | added_by_ai | Move the AI tall cabinet from the middle of the room to the north wall so it no longer blocks the walkway between island and dining area. |  | ![](images/r1_080_move_piece_before_r_L-1b_acik_mutfak_2.png) |  |
| 647 | remove_piece | {"piece_id": "f_L1_003", "reason": "The plan crop shows f_L1_003 is a dashed outline enclosing the two drawn sofas and the round table — it is a grouping/zone b | False | no_change: f_L1_003 is not built already | 22.0 -> 22.0 | adjusted_by_ai | The plan crop shows f_L1_003 is a dashed outline enclosing the two drawn sofas and the round table — it is a grouping/zone boundary, not furniture, and it renders as an implausible solid block in the lounge. |  | ![](images/r1_082_remove_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |  |
| 648 | change_type | {"piece_id": "f_L1_017", "type": "table_coffee", "reason": "The plan crop shows f_L1_017 is a round table with chairs around it (a game/activity table), so the  | False | room_type: table_coffee is not a piece a other room may hold here | 22.0 -> 22.0 | adjusted_by_ai | The plan crop shows f_L1_017 is a round table with chairs around it (a game/activity table), so the 1.63×1.52 m box is a table, not an unexplained block. |  | ![](images/r1_083_change_type_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |  |
| 649 | change_type | {"piece_id": "f_L1_005", "type": "bench", "reason": "The plan crop shows f_L1_005 is a long thin 3.66×0.4 m strip along the top wall — a bench, not an unexplain | False | room_type: bench is not a piece a other room may hold here | 22.0 -> 22.0 | adjusted_by_ai | The plan crop shows f_L1_005 is a long thin 3.66×0.4 m strip along the top wall — a bench, not an unexplained box. |  | ![](images/r1_084_change_type_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |  |
| 650 | change_type | {"piece_id": "f_L1_015", "type": "table_coffee", "reason": "The plan crop shows f_L1_015 is the round table drawn between the two sofas, so it is a coffee table | False | room_type: table_coffee is not a piece a other room may hold here | 22.0 -> 22.0 | adjusted_by_ai | The plan crop shows f_L1_015 is the round table drawn between the two sofas, so it is a coffee table. |  | ![](images/r1_085_change_type_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |  |
| 651 | change_type | {"piece_id": "f_L1_024", "type": "chair", "reason": "The plan crop shows f_L1_024 is one of the two drawn chairs at the bottom of the room, so the box is a chai | False | product_size: f_L1_024: 0.68 x 0.78 m does not fit a chair (size table) | 22.0 -> 22.0 | adjusted_by_ai | The plan crop shows f_L1_024 is one of the two drawn chairs at the bottom of the room, so the box is a chair. |  | ![](images/r1_086_change_type_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |  |
| 652 | move_piece | {"piece_id": "f_L1_010", "snap_wall_id": "w_L1_015", "offset": 1.8, "reason": "Snap the sofa's back onto the right wall to fix F3 (back 2.48 m off a wall)."} | False | snap: f_L1_010: no free place on wall w_L1_015 (doors, windows, at most 0.3 m from the drawn place) | 22.0 -> 22.0 | adjusted_by_ai | Snap the sofa's back onto the right wall to fix F3 (back 2.48 m off a wall). |  | ![](images/r1_088_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |  |
| 653 | move_piece | {"piece_id": "f_L1_011", "snap_wall_id": "w_L1_012", "offset": 5.7, "reason": "Snap the sofa's back onto the left wall to fix F3 (back 0.79 m off a wall)."} | False | snap: f_L1_011: no free place on wall w_L1_012 (doors, windows, at most 0.3 m from the drawn place) | 22.0 -> 22.0 | adjusted_by_ai | Snap the sofa's back onto the left wall to fix F3 (back 0.79 m off a wall). |  | ![](images/r1_089_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |  |
| 654 | move_piece | {"piece_id": "f_L1_010", "center": [12.4225, 4.0221], "reason": "Move the sofa so its back sits on the right wall (window wall) to fix F3."} | False | drawn_lock: f_L1_010: a drawn piece moves at most 0.3 m (this move: 1.46 m) | 22.0 -> 22.0 | adjusted_by_ai | Move the sofa so its back sits on the right wall (window wall) to fix F3. |  | ![](images/r1_090_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |  |
| 655 | move_piece | {"piece_id": "f_L1_011", "center": [8.2365, 5.9123], "reason": "Move the sofa so its back sits on the left wall to fix F3."} | False | drawn_lock: f_L1_011: a drawn piece moves at most 0.3 m (this move: 1.28 m) | 22.0 -> 22.0 | adjusted_by_ai | Move the sofa so its back sits on the left wall to fix F3. |  | ![](images/r1_091_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |  |
| 656 | change_type | {"piece_id": "f_L1_004", "type": "table_coffee", "reason": "The large central drawn box (4.49x3.02 m) is the activity table of the play/relax room, surrounded b | False | room_type: table_coffee is not a piece a other room may hold here | 22.0 -> 22.0 | adjusted_by_ai | The large central drawn box (4.49x3.02 m) is the activity table of the play/relax room, surrounded by the sofas and ottoman; it is not a rug. |  | ![](images/r1_092_change_type_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |  |
| 657 | change_type | {"piece_id": "f_L1_006", "type": "bench", "reason": "The long thin drawn box (3.66x0.4 m) along the bottom edge is a low bench, not an unexplained box."} | False | room_type: bench is not a piece a other room may hold here | 22.0 -> 22.0 | adjusted_by_ai | The long thin drawn box (3.66x0.4 m) along the bottom edge is a low bench, not an unexplained box. |  | ![](images/r1_093_change_type_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |  |
| 658 | resize_piece | {"piece_id": "f_L0_007", "size": [2.0, 1.6], "reason": "Shrink the drawn bed to a real double-bed size so the 0.9 m walkways from both doors to the window are n | True |  | 50.0 -> 87.0 | adjusted_by_ai | Shrink the drawn bed to a real double-bed size so the 0.9 m walkways from both doors to the window are no longer blocked. | refit | ![](images/r1_095_resize_piece_before_r_L0_e_yatak_odasi.png) | ![](images/r1_096_resize_piece_after_r_L0_e_yatak_odasi.png) |
| 659 | move_piece | {"piece_id": "f_L0_007", "center": [6.5865, 3.5159], "reason": "Shift the bed 0.3 m toward the window so the 0.9 m walkway from both doors to the window is clea | False | drawn_lock: f_L0_007: a drawn piece moves at most 0.3 m (this move: 0.36 m) | 87.0 -> 87.0 | adjusted_by_ai | Shift the bed 0.3 m toward the window so the 0.9 m walkway from both doors to the window is clear. |  | ![](images/r1_097_move_piece_before_r_L0_e_yatak_odasi.png) |  |
| 660 | move_piece | {"piece_id": "f_L0_007", "center": [6.5865, 3.5159], "reason": "Shift the bed 0.3 m toward the window so the 0.9 m walkway from both doors to the window is clea | False | drawn_lock: f_L0_007: a drawn piece moves at most 0.3 m (this move: 0.36 m) | 87.0 -> 87.0 | adjusted_by_ai | Shift the bed 0.3 m toward the window so the 0.9 m walkway from both doors to the window is clear. |  | ![](images/r1_098_move_piece_before_r_L0_e_yatak_odasi.png) |  |
| 661 | move_piece | {"piece_id": "f_L0_007", "center": [6.5865, 3.5159], "reason": "Shift the bed 0.3 m toward the window so the 0.9 m walkway from both doors to the window is clea | False | max_tries: f_L0_007 was edited 3 times in this round |  | adjusted_by_ai | Shift the bed 0.3 m toward the window so the 0.9 m walkway from both doors to the window is clear. |  |  |  |
| 662 | move_piece | {"piece_id": "f_L0_031", "center": [7.1615, 2.3601], "reason": "Move the floor lamp 0.3 m toward the window so it no longer overlaps the bed."} | False | f_L0_043: no_overlap, score: plausibility 87 -> 77 (F9 f_L0_043: nightstand f_L0_043 overlaps floor_lamp f_L0_031 by 0.10 m²) | 87.0 -> 77.0 | adjusted_by_ai | Move the floor lamp 0.3 m toward the window so it no longer overlaps the bed. |  | ![](images/r1_099_move_piece_before_r_L0_e_yatak_odasi.png) |  |
| 663 | move_piece | {"piece_id": "f_L0_032", "center": [7.1615, 5.1409], "reason": "Move the floor lamp 0.3 m toward the door wall so it no longer overlaps the bed."} | False | f_L0_044: no_overlap | 87.0 -> 97.0 | adjusted_by_ai | Move the floor lamp 0.3 m toward the door wall so it no longer overlaps the bed. |  | ![](images/r1_100_move_piece_before_r_L0_e_yatak_odasi.png) |  |
| 664 | move_piece | {"piece_id": "f_L0_031", "center": [7.1615, 2.2601], "reason": "Move the floor lamp 0.4 m toward the window so it clears both the bed and the nightstand."} | False | drawn_lock: f_L0_031: a drawn piece moves at most 0.3 m (this move: 0.40 m) | 87.0 -> 87.0 | adjusted_by_ai | Move the floor lamp 0.4 m toward the window so it clears both the bed and the nightstand. |  | ![](images/r1_101_move_piece_before_r_L0_e_yatak_odasi.png) |  |

Re-runs and renders:

| seq | kind | from | status | views | seconds | before | after | note |
|---|---|---|---|---|---|---|---|---|
| 307 | rerun | refit | failed | cam_r_L-1_salon_1, cam_r_L-1_salon_2, cam_r_L-1_salon_3 | 14.4 |  |  | refit refused the round's edits: 1 edit(s) rolled back |
| 308 | render |  | preview | cam_r_L-1_salon_1 |  | ![](images/r1_cam_r_L-1_salon_1_before.jpg) | ![](images/r1_cam_r_L-1_salon_1_after.jpg) |  |
| 309 | render |  | preview | cam_r_L-1_salon_2 |  | ![](images/r1_cam_r_L-1_salon_2_before.jpg) | ![](images/r1_cam_r_L-1_salon_2_after.jpg) |  |
| 310 | render |  | preview | cam_r_L-1_salon_3 |  | ![](images/r1_cam_r_L-1_salon_3_before.jpg) | ![](images/r1_cam_r_L-1_salon_3_after.jpg) |  |
| 665 | rerun | refit | ok | cam_r_L-1_salon_1, cam_r_L-1_salon_2, cam_r_L-1_salon_3, cam_r_L0_e_yatak_odasi_1, cam_r_L0_e_yatak_odasi_2, cam_r_L0_e_yatak_odasi_3 | 277.9 |  |  |  |
| 666 | render |  | preview | cam_r_L-1_salon_1 |  | ![](images/r1_cam_r_L-1_salon_1_before.jpg) | ![](images/r1_cam_r_L-1_salon_1_after.jpg) |  |
| 667 | render |  | preview | cam_r_L-1_salon_2 |  | ![](images/r1_cam_r_L-1_salon_2_before.jpg) | ![](images/r1_cam_r_L-1_salon_2_after.jpg) |  |
| 668 | render |  | preview | cam_r_L-1_salon_3 |  | ![](images/r1_cam_r_L-1_salon_3_before.jpg) | ![](images/r1_cam_r_L-1_salon_3_after.jpg) |  |
| 669 | render |  | preview | cam_r_L0_e_yatak_odasi_1 |  | ![](images/r1_cam_r_L0_e_yatak_odasi_1_before.jpg) | ![](images/r1_cam_r_L0_e_yatak_odasi_1_after.jpg) |  |
| 670 | render |  | preview | cam_r_L0_e_yatak_odasi_2 |  | ![](images/r1_cam_r_L0_e_yatak_odasi_2_before.jpg) | ![](images/r1_cam_r_L0_e_yatak_odasi_2_after.jpg) |  |
| 671 | render |  | preview | cam_r_L0_e_yatak_odasi_3 |  | ![](images/r1_cam_r_L0_e_yatak_odasi_3_before.jpg) | ![](images/r1_cam_r_L0_e_yatak_odasi_3_after.jpg) |  |

Stop: the re-run of the changed stages failed (1 edits accepted in 1 rounds)

## Round 2

| seq | critic | of | status | counts | note |
|---|---|---|---|---|---|
| 672 | code | plausibility | ok | {"critical": 0, "major": 81, "minor": 57} |  |
| 673 | code | exterior | ok | {"critical": 1, "major": 4, "minor": 2} |  |
| 674 | code | views | ok | {"critical": 0, "major": 0, "minor": 0} |  |
| 675 | vision | r_L-1_salon | ok | {"kept": 3, "dropped": 0} |  |
| 676 | vision | r_L-1_salon_2 | ok | {"kept": 0, "dropped": 12} |  |
| 677 | vision | r_L0_e_yatak_odasi | ok | {"kept": 0, "dropped": 2} |  |

Findings: 212 (14 dropped).

| seq | source | check | severity | target | finding | dropped |
|---|---|---|---|---|---|---|
| 678 | code | F1 | minor | f_L-1_024 | wardrobe is not a piece of a living room |  |
| 679 | code | F3 | major | f_L-1_053 | sofa_corner: its back is not on a wall (1.10 m off) |  |
| 680 | code | F4 | major | f_L-1_049 | armchair does not face its group (f_L-1_053, f_L-1_061) |  |
| 681 | code | F4 | major | f_L-1_053 | sofa_corner does not face its group (f_L-1_089, f_L-1_073) |  |
| 682 | code | F4 | major | f_L-1_089 | tv_unit stands behind the back of f_L-1_090, f_L-1_049, looking at it |  |
| 683 | code | F4 | major | f_L-1_090 | armchair does not face its group (f_L-1_061, f_L-1_053) |  |
| 684 | code | F5 | minor | f_L-1_061 | sofa without a coffee table |  |
| 685 | code | F6 | major | f_L-1_049 | armchair: the free zone in front of it is reaches out of the room |  |
| 686 | code | F6 | major | f_L-1_053 | no 0.9 m walkway from o_L-1_001 to win_L-1_001 (blocked by f_L-1_053) |  |
| 687 | code | F7 | major | f_L-1_063 | floor_lamp (1.60 m) stands in front of window win_L-1_001 (sill 0.90 m) |  |
| 688 | code | F8 | major | f_L-1_073 | table_coffee stands alone in the room (no wall, no sofa / sofa_corner / armchair within 1.5 m) |  |
| 689 | code | F9 | major | f_L-1_021 | an unexplained drawn box (3.33 m², type unknown) is built |  |
| 690 | code | F9 | major | f_L-1_024 | wardrobe reaches 0.05 m² through the room outline |  |
| 691 | code | F9 | minor | f_L-1_060 | an unexplained drawn box (0.62 m², type unknown) is built |  |
| 692 | code | F9 | minor | f_L-1_070 | an unexplained drawn box (0.37 m², type unknown) is built |  |
| 693 | code | F9 | minor | f_L-1_071 | an unexplained drawn box (0.37 m², type unknown) is built |  |
| 694 | code | F9 | minor | f_L-1_087 | an unexplained drawn box (0.29 m², type unknown) is built |  |
| 695 | code | F1 | minor | f_L-1_023 | wardrobe is not a piece of a living room |  |
| 696 | code | F3 | major | f_L-1_054 | sofa_corner: its back is not on a wall (1.10 m off) |  |
| 697 | code | F3 | major | f_L-1_062 | sofa: its back is not on a wall (2.39 m off) |  |
| 698 | code | F4 | major | f_L-1_050 | armchair does not face its group (f_L-1_054, f_L-1_062) |  |
| 699 | code | F4 | major | f_L-1_054 | sofa_corner does not face its group (f_L-1_102, f_L-1_074) |  |
| 700 | code | F4 | major | f_L-1_062 | sofa does not face its group (f_L-1_102, f_L-1_074) |  |
| 701 | code | F4 | major | f_L-1_102 | tv_unit stands behind the back of f_L-1_103, f_L-1_050, looking at it |  |
| 702 | code | F4 | major | f_L-1_103 | armchair does not face its group (f_L-1_062, f_L-1_054) |  |
| 703 | code | F5 | minor | f_L-1_062 | sofa without a coffee table |  |
| 704 | code | F6 | major | f_L-1_050 | armchair: the free zone in front of it is reaches out of the room |  |
| 705 | code | F6 | major | f_L-1_054 | no 0.9 m walkway from o_L-1_002 to win_L-1_002 (blocked by f_L-1_054) |  |
| 706 | code | F7 | major | f_L-1_057 | floor_lamp (1.60 m) stands in front of window win_L-1_002 (sill 0.90 m) |  |
| 707 | code | F7 | major | f_L-1_065 | floor_lamp (1.60 m) stands in front of window win_L-1_002 (sill 0.90 m) |  |
| 708 | code | F8 | major | f_L-1_074 | table_coffee stands alone in the room (no wall, no sofa / sofa_corner / armchair within 1.5 m) |  |
| 709 | code | F9 | major | f_L-1_022 | an unexplained drawn box (3.33 m², type unknown) is built |  |
| 710 | code | F9 | major | f_L-1_023 | wardrobe reaches 0.05 m² through the room outline |  |
| 711 | code | F9 | minor | f_L-1_058 | an unexplained drawn box (0.62 m², type unknown) is built |  |
| 712 | code | F9 | minor | f_L-1_069 | an unexplained drawn box (0.37 m², type unknown) is built |  |
| 713 | code | F9 | minor | f_L-1_072 | an unexplained drawn box (0.37 m², type unknown) is built |  |
| 714 | code | F9 | minor | f_L-1_088 | an unexplained drawn box (0.29 m², type unknown) is built |  |
| 715 | code | F3 | major | f_L-1_008 | stove: its back is not on a wall (0.06 m off) |  |
| 716 | code | F5 | minor | f_L-1_095 | dining table with 2 of 6 chairs |  |
| 717 | code | F7 | major | f_L-1_067 | fridge (1.80 m) stands in front of window win_L-1_003 (sill 0.90 m) |  |
| 718 | code | F9 | minor | f_L-1_006 | an unexplained drawn box (0.10 m², type unknown) is built |  |
| 719 | code | F9 | minor | f_L-1_007 | an unexplained drawn box (0.10 m², type unknown) is built |  |
| 720 | code | F9 | major | f_L-1_008 | stove f_L-1_008 overlaps kitchen_counter f_L-1_002 by 0.41 m² |  |
| 721 | code | F9 | major | f_L-1_067 | fridge f_L-1_067 overlaps kitchen_counter f_L-1_003 by 0.39 m² |  |
| 722 | code | R3 | minor | d_L-1_003 | door d_L-1_003 swings into f_L-1_001 on one hinge side; the other hinge side is free |  |
| 723 | code | F3 | major | f_L-1_017 | stove: its back is not on a wall (0.06 m off) |  |
| 724 | code | F5 | minor | f_L-1_107 | dining table with 2 of 6 chairs |  |
| 725 | code | F7 | major | f_L-1_068 | fridge (1.80 m) stands in front of window win_L-1_004 (sill 0.90 m) |  |
| 726 | code | F9 | minor | f_L-1_015 | an unexplained drawn box (0.10 m², type unknown) is built |  |
| 727 | code | F9 | minor | f_L-1_016 | an unexplained drawn box (0.10 m², type unknown) is built |  |
| 728 | code | F9 | major | f_L-1_017 | stove f_L-1_017 overlaps kitchen_counter f_L-1_011 by 0.41 m² |  |
| 729 | code | F9 | major | f_L-1_068 | fridge f_L-1_068 overlaps kitchen_counter f_L-1_012 by 0.39 m² |  |
| 730 | code | R3 | minor | d_L-1_004 | door d_L-1_004 swings into f_L-1_010 on one hinge side; the other hinge side is free |  |
| 731 | code | F3 | major | f_L-1_056 | bathtub: its back is not on a wall (0.09 m off) |  |
| 732 | code | F4 | major | f_L-1_056 | bathtub faces a wall 0.00 m in front of it |  |
| 733 | code | R3 | minor | d_L-1_001 | door d_L-1_001 swings into f_L-1_026 on one hinge side; the other hinge side is free |  |
| 734 | code | R3 | minor | d_L-1_002 | door d_L-1_002 swings into f_L-1_025 on one hinge side; the other hinge side is free |  |
| 735 | code | F9 | major | f_L-1b_013 | stove f_L-1b_013 overlaps kitchen_counter f_L-1b_009 by 0.41 m² |  |
| 736 | code | F9 | major | f_L-1b_040 | an unexplained drawn box (1.91 m², type unknown) is built |  |
| 737 | code | F9 | major | f_L-1b_044 | an unexplained drawn box (1.34 m², type unknown) is built |  |
| 738 | code | F9 | minor | f_L-1b_047 | an unexplained drawn box (0.35 m², type unknown) is built |  |
| 739 | code | F9 | minor | f_L-1b_048 | an unexplained drawn box (0.62 m², type unknown) is built |  |
| 740 | code | F9 | minor | f_L-1b_049 | an unexplained drawn box (0.65 m², type unknown) is built |  |
| 741 | code | F9 | minor | f_L-1b_050 | an unexplained drawn box (0.65 m², type unknown) is built |  |
| 742 | code | F9 | major | f_L-1b_054 | fridge f_L-1b_054 overlaps kitchen_counter f_L-1b_010 by 0.39 m² |  |
| 743 | code | F9 | minor | f_L-1b_056 | an unexplained drawn box (0.16 m², type unknown) is built |  |
| 744 | code | F9 | major | f_L-1b_007 | stove f_L-1b_007 overlaps kitchen_counter f_L-1b_003 by 0.41 m² |  |
| 745 | code | F9 | major | f_L-1b_043 | an unexplained drawn box (1.34 m², type unknown) is built |  |
| 746 | code | F9 | minor | f_L-1b_045 | an unexplained drawn box (0.35 m², type unknown) is built |  |
| 747 | code | F9 | minor | f_L-1b_046 | an unexplained drawn box (0.62 m², type unknown) is built |  |
| 748 | code | F9 | minor | f_L-1b_051 | an unexplained drawn box (0.65 m², type unknown) is built |  |
| 749 | code | F9 | minor | f_L-1b_052 | an unexplained drawn box (0.65 m², type unknown) is built |  |
| 750 | code | F9 | major | f_L-1b_053 | fridge f_L-1b_053 overlaps kitchen_counter f_L-1b_004 by 0.39 m² |  |
| 751 | code | F9 | minor | f_L-1b_055 | an unexplained drawn box (0.16 m², type unknown) is built |  |
| 752 | code | F4 | major | f_L-1b_064 | chair faces a wall 0.11 m in front of it |  |
| 753 | code | F5 | minor | f_L-1b_061 | desk without a chair |  |
| 754 | code | F5 | minor | f_L-1b_065 | dining table with 1 of 4 chairs |  |
| 755 | code | F8 | major | f_L-1b_063 | armchair stands alone in the room (no wall, no sofa / sofa_corner / armchair within 2.0 m) |  |
| 756 | code | F4 | major | f_L-1b_069 | chair faces a wall 0.11 m in front of it |  |
| 757 | code | F5 | minor | f_L-1b_066 | desk without a chair |  |
| 758 | code | F5 | minor | f_L-1b_070 | dining table with 1 of 4 chairs |  |
| 759 | code | F8 | major | f_L-1b_068 | armchair stands alone in the room (no wall, no sofa / sofa_corner / armchair within 2.0 m) |  |
| 760 | code | F3 | major | f_L-1b_038 | toilet: its back is not on a wall (0.02 m off) |  |
| 761 | code | F3 | major | f_L-1b_042 | bathtub: its back is not on a wall (0.09 m off) |  |
| 762 | code | F4 | major | f_L-1b_042 | bathtub faces a wall 0.00 m in front of it |  |
| 763 | code | R3 | minor | d_L-1b_002 | door d_L-1b_002 swings into f_L-1b_036 on one hinge side; the other hinge side is free |  |
| 764 | code | F3 | major | f_L-1b_037 | toilet: its back is not on a wall (0.02 m off) |  |
| 765 | code | R3 | minor | d_L-1b_003 | door d_L-1b_003 swings into f_L-1b_035 on one hinge side; the other hinge side is free |  |
| 766 | code | F4 | major | f_L0_041 | bench faces a wall 0.04 m in front of it |  |
| 767 | code | F5 | minor | f_L0_007 | bed_double with 1 of 2 nightstands |  |
| 768 | code | F9 | major | f_L0_032 | floor_lamp f_L0_032 overlaps bed_double f_L0_007 by 0.10 m² |  |
| 769 | code | F6 | major | f_L0_008 | no 0.9 m walkway from d_L0_003 to d_L0_004 (blocked by f_L0_008) |  |
| 770 | code | F6 | major | f_L0_008 | no 0.9 m walkway from d_L0_003 to win_L0_003 (blocked by f_L0_008) |  |
| 771 | code | F6 | major | f_L0_008 | no 0.9 m walkway from d_L0_004 to win_L0_003 (blocked by f_L0_008) |  |
| 772 | code | F9 | major | f_L0_033 | floor_lamp f_L0_033 overlaps bed_double f_L0_008 by 0.17 m² |  |
| 773 | code | F9 | major | f_L0_034 | floor_lamp f_L0_034 overlaps bed_double f_L0_008 by 0.22 m² |  |
| 774 | code | F4 | major | f_L0_053 | bench faces a wall 0.04 m in front of it |  |
| 775 | code | F2 | major | f_L0_013 | shower 1.40 x 0.60 m is outside the type's product sizes |  |
| 776 | code | F3 | minor | f_L0_013 | shower: its back is not on a wall (0.07 m off) |  |
| 777 | code | F4 | major | f_L0_013 | shower faces a wall 0.10 m in front of it |  |
| 778 | code | F2 | major | f_L0_014 | shower 1.40 x 0.60 m is outside the type's product sizes |  |
| 779 | code | F3 | minor | f_L0_014 | shower: its back is not on a wall (0.07 m off) |  |
| 780 | code | F6 | major | f_L0_009 | wardrobe: the free zone in front of it is blocked by f_L0_029 |  |
| 781 | code | F6 | major | f_L0_011 | wardrobe: the free zone in front of it is blocked by f_L0_028 |  |
| 782 | code | F3 | major | f_L0_025 | bathtub: its back is not on a wall (0.09 m off) |  |
| 783 | code | F4 | major | f_L0_025 | bathtub faces a wall 0.00 m in front of it |  |
| 784 | code | R3 | minor | d_L0_007 | door d_L0_007 swings into f_L0_003 on one hinge side; the other hinge side is free |  |
| 785 | code | R3 | minor | d_L0_008 | door d_L0_008 swings into f_L0_005 on one hinge side; the other hinge side is free |  |
| 786 | code | F1 | minor | f_L1_009 | sofa is not a piece of a other room |  |
| 787 | code | F1 | minor | f_L1_012 | sofa is not a piece of a other room |  |
| 788 | code | F1 | minor | f_L1_027 | ottoman is not a piece of a other room |  |
| 789 | code | F3 | major | f_L1_009 | sofa: its back is not on a wall (2.48 m off) |  |
| 790 | code | F3 | major | f_L1_012 | sofa: its back is not on a wall (0.79 m off) |  |
| 791 | code | F4 | major | f_L1_029 | armchair does not face its group (f_L1_009, f_L1_012) |  |
| 792 | code | F8 | major | f_L1_030 | chair stands alone in the room (no wall, no table_dining / desk / kitchen_island within 0.8 m) |  |
| 793 | code | F9 | major | f_L1_005 | an unexplained drawn box (1.47 m², type unknown) is built |  |
| 794 | code | F9 | minor | f_L1_015 | an unexplained drawn box (0.71 m², type unknown) is built |  |
| 795 | code | F9 | major | f_L1_017 | an unexplained drawn box (2.48 m², type unknown) is built |  |
| 796 | code | F9 | minor | f_L1_024 | an unexplained drawn box (0.53 m², type unknown) is built |  |
| 797 | code | F9 | minor | f_L1_025 | an unexplained drawn box (0.53 m², type unknown) is built |  |
| 798 | code | F1 | minor | f_L1_010 | sofa is not a piece of a other room |  |
| 799 | code | F1 | minor | f_L1_011 | sofa is not a piece of a other room |  |
| 800 | code | F1 | minor | f_L1_028 | ottoman is not a piece of a other room |  |
| 801 | code | F3 | major | f_L1_010 | sofa: its back is not on a wall (2.48 m off) |  |
| 802 | code | F3 | major | f_L1_011 | sofa: its back is not on a wall (0.79 m off) |  |
| 803 | code | F4 | major | f_L1_033 | armchair does not face its group (f_L1_010, f_L1_011) |  |
| 804 | code | F8 | major | f_L1_034 | chair stands alone in the room (no wall, no table_dining / desk / kitchen_island within 0.8 m) |  |
| 805 | code | F9 | major | f_L1_006 | an unexplained drawn box (1.47 m², type unknown) is built |  |
| 806 | code | F9 | minor | f_L1_016 | an unexplained drawn box (0.71 m², type unknown) is built |  |
| 807 | code | F9 | major | f_L1_018 | an unexplained drawn box (2.48 m², type unknown) is built |  |
| 808 | code | F9 | minor | f_L1_023 | an unexplained drawn box (0.53 m², type unknown) is built |  |
| 809 | code | F9 | minor | f_L1_026 | an unexplained drawn box (0.53 m², type unknown) is built |  |
| 810 | code | F3 | major | f_L1_013 | toilet: its back is not on a wall (0.02 m off) |  |
| 811 | code | F3 | major | f_L1_019 | bathtub: its back is not on a wall (0.09 m off) |  |
| 812 | code | F4 | major | f_L1_019 | bathtub faces a wall 0.00 m in front of it |  |
| 813 | code | R3 | minor | d_L1_004 | door d_L1_004 swings into f_L1_007 on one hinge side; the other hinge side is free |  |
| 814 | code | F3 | major | f_L1_014 | toilet: its back is not on a wall (0.02 m off) |  |
| 815 | code | R3 | minor | d_L1_005 | door d_L1_005 swings into f_L1_008 on one hinge side; the other hinge side is free |  |
| 816 | code | X2 | minor | ro_001 | roof terrace ro_001 (r_L1_teras): the plan labels a terrace, the section r6 draws the roof closed over it; cut into the roof (brief roof_terraces: auto: the plan draws r_L1_teras as a room with a door to it (d_L1_003)) |  |
| 817 | code | X2 | minor | ro_002 | roof terrace ro_002 (r_L1_teras_2): the plan labels a terrace, the section r6 draws the roof closed over it; cut into the roof (brief roof_terraces: auto: the plan draws r_L1_teras_2 as a room with a door to it (d_L1_006)) |  |
| 818 | code | X2 | major | d_L1_004 | door height not drawn: its top 2.10 m above the floor would reach over the roof underside (1.10 m) at its wall; clipped 0.05 m under it (docs/milestone11.md §1.1 E8); still lower than a usable door (needs a dormer: review) |  |
| 819 | code | X2 | major | d_L1_005 | door height not drawn: its top 2.10 m above the floor would reach over the roof underside (1.10 m) at its wall; clipped 0.05 m under it (docs/milestone11.md §1.1 E8); still lower than a usable door (needs a dormer: review) |  |
| 820 | code | X2 | critical | dec_L1_011 | decor_dec_L1_011 pokes through the roof (top 5.35 m) |  |
| 821 | code | X3 | major | r_L0_yatak_odasi_3 | r_L0_yatak_odasi_3 (bedroom): 7.7 m of outer wall with no window or door: a blank facade |  |
| 822 | code | X3 | major | r_L0_yatak_odasi_4 | r_L0_yatak_odasi_4 (bedroom): 7.7 m of outer wall with no window or door: a blank facade |  |
| 823 | vision | F9 | major | f_L-1_027 | The dining table is rendered as a giant, oversized slab that dominates the room, far exceeding the scale of the surrounding chairs and the room's proportions. |  |
| 824 | vision | F9 | major | f_L-1_053 | The corner sofa is rendered as a massive, monolithic block that looks like a wall or a giant box rather than a piece of furniture, obscuring the seating area. |  |
| 825 | vision | F9 | minor | f_L-1_063 | The floor lamp is rendered with a strange, thin vertical spike extending from the top of the lampshade, which is not a realistic design feature. |  |
| 826 | vision | F9 | major | f_L-1_094 | The tall cabinet (f_L-1_094) is rendered as a solid, featureless white block that looks like a placeholder or a rendering error, rather than a finished piece of furniture. |  |
| 827 | vision | F9 | minor | f_L-1_018 | An unexplained drawn box (0.06 m², type unknown) is built. |  |
| 828 | vision | F9 | minor | f_L-1_082 | An unexplained drawn box (0.15 m², type unknown) is built. |  |
| 829 | vision | F9 | minor | f_L-1_084 | An unexplained drawn box (0.15 m², type unknown) is built. |  |
| 830 | vision | F9 | minor | f_L-1_086 | An unexplained drawn box (0.06 m², type unknown) is built. |  |
| 831 | vision | F1 | major | f_L-1_020 | A stair (f_L-1_020) is placed inside a corridor/hall room, which is an incorrect fixture type for this space. |  |
| 832 | vision | F9 | critical | f_L-1_020 | The stair (f_L-1_020) is drawn as a giant box that covers the majority of the room's floor area, which is physically impossible and visually incorrect. |  |
| 833 | vision | F1 | major | f_L-1_101 | A console table is placed in a hallway (Koridor), which is an unusual furniture choice for this room type. |  |
| 834 | vision | F9 | major | f_L-1_056 | The bathtub is rendered as a simple open box (Image 3) without a drain, faucet, or internal basin, making it look like a storage bin rather than a functional fixture. |  |
| 835 | vision | F9 | major | f_L-1_026 | The washbasin is rendered as a flat, empty rectangular depression in the countertop (Images 2 & 3) with no visible bowl or basin depth, making it look like a cutout rather than a sink. |  |
| 836 | vision | F9 | major | f_L-1b_002 | A large unexplained box (5.54x2.77 m) is built in the middle of the room, which is not a standard furniture item and obstructs the space. |  |
| 837 | vision | F9 | major | f_L-1b_001 | A large unexplained box (5.54x2.77 m) is built in the center of the room, overlapping the kitchen island and bar stools. |  |
| 838 | vision | F9 | major | f_L-1b_039 | A large unexplained box (2.13x0.9 m) is built in the center of the room, overlapping the kitchen island and bar stools. |  |
| 839 | vision | F9 | major | f_L-1b_076 | A tall cabinet is built in the middle of the room, blocking the walkway between the kitchen island and the dining area. |  |
| 840 | vision | F9 | major | f_L-1b_077 | A bar stool is built in the middle of the room, not adjacent to a counter or island. |  |
| 841 | vision | F9 | major | f_L-1b_078 | A bar stool is built in the middle of the room, not adjacent to a counter or island. |  |
| 842 | vision | F9 | major | f_L-1b_079 | A bar stool is built in the middle of the room, not adjacent to a counter or island. |  |
| 843 | vision | F9 | major | f_L-1b_080 | A bar stool is built in the middle of the room, not adjacent to a counter or island. |  |
| 844 | vision | F4 | major | f_L-1b_061 | The desk is facing a wall instead of a window or open space, which is an incorrect orientation for a workspace. |  |
| 845 | vision | F1 | major | f_L-1b_075 | A console table is placed in a corridor (hall), which is an unusual fixture for this room type. |  |
| 846 | vision | F1 | major | f_L-1b_015 | A stair (f_L-1b_015) is placed inside a corridor/hall room, which is an incorrect fixture type for this space. |  |
| 847 | vision | F9 | critical | f_L-1b_015 | The stair piece (f_L-1b_015) is drawn as a large green box that extends through the room's boundary wall, which is a clear geometric error. |  |
| 848 | vision | F9 | major | f_L-1b_042 | The bathtub (f_L-1b_042) is placed in the corner of the room, but its front is facing directly into the wall with no clearance, making it unusable. |  |
| 849 | vision | F9 | major | f_L-1b_038 | The toilet (f_L-1b_038) is placed in the corner of the room, but its front is facing directly into the wall with no clearance, making it unusable. |  |
| 850 | vision | F9 | critical | f_L-1b_041 | The bathtub (f_L-1b_041) is drawn as a giant box that extends significantly beyond the room's outer wall on the left side. |  |
| 851 | vision | F9 | critical | f_L-1b_035 | The washbasin (f_L-1b_035) is drawn as a box that extends beyond the room's outer wall on the right side. |  |
| 852 | vision | F9 | major | f_L-1b_037 | The toilet (f_L-1b_037) is drawn as a box that extends beyond the room's outer wall on the bottom side. |  |
| 853 | vision | F1 | minor | f_L0_053 | A bench is an unusual piece of furniture for a bedroom, especially placed at the foot of the bed. |  |
| 854 | vision | F1 | major | f_L0_035 | A console table is placed in a narrow corridor (hall), which is an inappropriate furniture type for this room type. |  |
| 855 | vision | F1 | major | f_L0_036 | A shoe cabinet is placed in a narrow corridor (hall), which is an inappropriate furniture type for this room type. |  |
| 856 | vision | F9 | major | f_L0_006 | The washbasin is rendered as a solid block with a recessed top surface, resembling a bathtub or a box, rather than a functional sink with a basin and faucet. |  |
| 857 | vision | F9 | major | f_L0_015 | The toilet is rendered as a simple rectangular box with a handle, completely missing the bowl, seat, and tank structure of a real toilet. |  |
| 858 | vision | F9 | minor | f_L0_056 | A bench is an unusual piece of furniture for a bedroom. |  |
| 859 | vision | F9 | critical | f_L0_002 | The stair piece (f_L0_002) is drawn as a single line with an arrow, which is a debug marker or a failed geometry representation, not a solid piece of furniture. |  |
| 860 | vision | F9 | major | o_L0_002 | The door opening (o_L0_002) is represented by a single orange line on the wall without a door leaf or swing arc, making it impossible to verify if the door opens correctly. |  |
| 861 | vision | F9 | major | f_L0_003 | The washbasin is rendered as a large, deep rectangular basin (resembling a small pool or trough) rather than a standard sink, which is a clear visual error in the model. |  |
| 862 | vision | F9 | major | f_L0_003 | The washbasin is rendered as a large, deep rectangular basin (resembling a small pool or trough) rather than a standard sink, which is a clear visual error in the model. |  |
| 863 | vision | F9 | major | f_L1_003 | The large box (f_L1_003) is rendered as a solid, opaque block in the middle of the room, which is not a plausible piece of furniture for a lounge area. |  |
| 864 | vision | F9 | major | f_L1_004 | An unexplained drawn box (13.56 m², type unknown) is built. |  |
| 865 | vision | F9 | minor | f_L1_033 | An unexplained drawn box (0.81 m², type unknown) is built. |  |
| 866 | vision | F1 | major | f_L1_002 | A full staircase is placed inside a 15.3 m2 corridor/hall, which is an inappropriate fixture for this room type. |  |
| 867 | vision | F1 | major | f_L1_036 | A console table is placed in a corridor (hall). This is an unusual fixture for a circulation space and is likely an AI hallucination or misclassification of a wall element. |  |
| 868 | vision | F4 | major | f_L1_007 | The washbasin is placed with its front facing the wall (90 degrees), making it unusable. It should face the open space of the room. |  |
| 869 | vision | F9 | major | f_L1_008 | The washbasin (f_L1_008) is placed in the middle of the room, floating away from any wall, which is unusual for a bathroom fixture. |  |
| 870 | vision | X3 | major | building | The main entrance door is not visible at grade on the front facade; the ground floor appears to have only windows and no clear entry point. |  |
| 871 | vision | X2 | critical | building | The building is described as having 4 levels, but the render only shows a single-story structure with a roof, missing the upper three floors. |  |
| 872 | vision | X2 | critical | building | A vertical element (likely a chimney or vent) is clearly poking through the roof surface. |  |
| 873 | vision | X3 | major | building | The main facade facing the camera is almost entirely blank, with only two doors and no visible windows, which is implausible for a multi-story building. |  |
| 874 | vision | X6 | major | ext_5 | The camera is positioned at a high angle looking down at the building, rather than at the required eye level (1.5-1.7 m). This results in a bird's-eye view where the roof dominates the composition and the vertical lines of the building appear to converge. |  |
| 875 | vision | X6 | major | ext_6 | The camera is positioned at a direct frontal angle, showing only one facade. The checklist requires a 3/4 corner view where two facades are visible. |  |
| 876 | vision | F9 | major | f_L-1_022 | A large unexplained box (3.33 m²) is built in the room, which is not a standard furniture item for a living room. | duplicate of a code finding |
| 877 | vision | F9 | major | f_L-1_023 | The wardrobe is drawn extending through the room's wall outline. | duplicate of a code finding |
| 878 | vision | F3 | major | f_L-1_054 | The corner sofa is floating in the middle of the room with its back 1.10 m away from the nearest wall. | duplicate of a code finding |
| 879 | vision | F3 | major | f_L-1_062 | The sofa is floating in the middle of the room with its back 2.39 m away from the nearest wall. | duplicate of a code finding |
| 880 | vision | F4 | major | f_L-1_050 | The armchair is facing away from the main seating group (sofa and coffee table). | duplicate of a code finding |
| 881 | vision | F4 | major | f_L-1_054 | The corner sofa is facing the wrong way, not towards the TV unit or coffee table. | duplicate of a code finding |
| 882 | vision | F4 | major | f_L-1_062 | The sofa is facing the wrong way, not towards the TV unit or coffee table. | duplicate of a code finding |
| 883 | vision | F4 | major | f_L-1_102 | The TV unit is positioned behind the armchairs, facing the wrong direction for the seating group. | duplicate of a code finding |
| 884 | vision | F4 | major | f_L-1_103 | The armchair is facing away from the main seating group (sofa and coffee table). | duplicate of a code finding |
| 885 | vision | F5 | minor | f_L-1_062 | The sofa is not part of a complete group, as it lacks a coffee table in front of it. | duplicate of a code finding |
| 886 | vision | F6 | major | f_L-1_050 | The free zone in front of the armchair extends outside the room boundaries. | duplicate of a code finding |
| 887 | vision | F6 | major | f_L-1_054 | The corner sofa blocks the 0.9 m walkway between the door and the window. | duplicate of a code finding |
| 888 | vision | F9 | major | f_L0_032 | The floor lamp (f_L0_032) is positioned directly on top of the bed (f_L0_007), overlapping the mattress area. | duplicate of a code finding |
| 889 | vision | F5 | minor | f_L0_007 | The bed is missing a nightstand on the left side (from the foot of the bed), leaving the group incomplete. | duplicate of a code finding |

Edits:

| seq | tool | args | accepted | failed checks | score | label | reason | re-run from | before | after |
|---|---|---|---|---|---|---|---|---|---|---|
| 890 | resize_piece | {"piece_id": "f_L-1b_041", "size": [1.7, 0.75], "reason": "Drawn bathtub box (1.83 m) extends past the left outer wall; resize to a standard 1.70 m tub so it fi | False | drawn_lock: f_L-1b_041: drawn fixed equipment keeps its drawn size | 87.0 -> 87.0 | adjusted_by_ai | Drawn bathtub box (1.83 m) extends past the left outer wall; resize to a standard 1.70 m tub so it fits inside the room. |  | ![](images/r2_005_resize_piece_before_r_L-1b_banyo_2.png) |  |
| 891 | resize_piece | {"piece_id": "f_L-1b_035", "size": [0.6, 0.45], "reason": "Drawn washbasin box (1.0 m wide) extends past the right outer wall; resize to a standard 0.60 m basin | False | drawn_lock: f_L-1b_035: drawn fixed equipment keeps its drawn size | 87.0 -> 87.0 | adjusted_by_ai | Drawn washbasin box (1.0 m wide) extends past the right outer wall; resize to a standard 0.60 m basin so it fits inside the room. |  | ![](images/r2_006_resize_piece_before_r_L-1b_banyo_2.png) |  |
| 892 | move_piece | {"piece_id": "f_L-1b_037", "center": [9.1208, 10.215], "reason": "Snap the toilet back onto the bottom wall (it was 0.02 m off) and pull it inside the room so i | False | drawn_lock: f_L-1b_037: drawn fixed equipment (toilet) is never moved | 87.0 -> 87.0 | adjusted_by_ai | Snap the toilet back onto the bottom wall (it was 0.02 m off) and pull it inside the room so it no longer crosses the outer wall. |  | ![](images/r2_007_move_piece_before_r_L-1b_banyo_2.png) |  |
| 893 | remove_piece | {"piece_id": "f_L-1_020", "reason": "The 2.71x2.10 m 'stair' box covers ~47% of this 11.9 m² corridor and is not a real stair: the plan crop shows no treads/ris | False | drawn_lock: f_L-1_020: drawn fixed equipment (stair) is never removed | 100.0 -> 100.0 | adjusted_by_ai | The 2.71x2.10 m 'stair' box covers ~47% of this 11.9 m² corridor and is not a real stair: the plan crop shows no treads/risers in this area, the corridor label (7 m²) only reconciles if the box is excluded, and a stair of this size would be a fixed structural element that cannot sit inside a hall. I |  | ![](images/r2_009_remove_piece_before_r_L-1_koridor.png) |  |
| 894 | resize_piece | {"piece_id": "f_L-1_020", "size": [1.2, 2.4], "reason": "The drawn 2.71x2.10 m stair box covers ~47% of the 11.9 m² corridor, which is physically impossible; re | False | drawn_lock: f_L-1_020: drawn fixed equipment keeps its drawn size | 100.0 -> 100.0 | adjusted_by_ai | The drawn 2.71x2.10 m stair box covers ~47% of the 11.9 m² corridor, which is physically impossible; resizing to a real straight-run stair footprint (1.2 m wide x 2.4 m long) keeps the drawn stair while making it plausible. |  | ![](images/r2_010_resize_piece_before_r_L-1_koridor.png) |  |
| 895 | move_piece | {"piece_id": "f_L-1_020", "center": [9.1143, 8.6436], "reason": "No-op move to confirm the drawn stair's locked position; the oversized footprint is a drawing a | False | drawn_lock: f_L-1_020: drawn fixed equipment (stair) is never moved | 100.0 -> 100.0 | adjusted_by_ai | No-op move to confirm the drawn stair's locked position; the oversized footprint is a drawing artifact that cannot be resized or removed under the drawn-lock rules. |  | ![](images/r2_011_move_piece_before_r_L-1_koridor.png) |  |
| 896 | remove_piece | {"piece_id": "f_L-1b_015", "reason": "The stair box (2.71×2.1 m) is drawn as a plain green rectangle with no treads, landing or direction markings in the plan c | False | drawn_lock: f_L-1b_015: drawn fixed equipment (stair) is never removed | 100.0 -> 100.0 | adjusted_by_ai | The stair box (2.71×2.1 m) is drawn as a plain green rectangle with no treads, landing or direction markings in the plan crop, and it extends through the room's boundary wall; it is a mis-extracted hatch/box, not a real stair, and a stair is not a valid fixture for this corridor. |  | ![](images/r2_013_remove_piece_before_r_L-1b_koridor_2.png) |  |
| 897 | resize_piece | {"piece_id": "f_L-1b_015", "size": [1.5, 1.5], "reason": "Shrink the stair to a real stairwell size so it no longer extends through the room's boundary wall (th | False | drawn_lock: f_L-1b_015: drawn fixed equipment keeps its drawn size | 100.0 -> 100.0 | adjusted_by_ai | Shrink the stair to a real stairwell size so it no longer extends through the room's boundary wall (the drawn 2.71×2.1 m box was a mis-extracted hatch). |  | ![](images/r2_014_resize_piece_before_r_L-1b_koridor_2.png) |  |
| 898 | move_piece | {"piece_id": "f_L-1b_015", "center": [9.1143, 8.6436], "reason": "Re-assert the stair's drawn centre so the layout engine re-clips the footprint to the room bou | False | drawn_lock: f_L-1b_015: drawn fixed equipment (stair) is never moved | 100.0 -> 100.0 | adjusted_by_ai | Re-assert the stair's drawn centre so the layout engine re-clips the footprint to the room boundary, removing the part that pokes through the wall. |  | ![](images/r2_015_move_piece_before_r_L-1b_koridor_2.png) |  |
| 899 | change_type | {"piece_id": "f_L-1b_015", "type": "tall_cabinet", "reason": "The drawn box has no treads, landing or direction markings in the plan crop and is not a valid sta | False | max_tries: f_L-1b_015 was edited 3 times in this round |  | adjusted_by_ai | The drawn box has no treads, landing or direction markings in the plan crop and is not a valid stair for this corridor; re-typing it as a tall cabinet (a storage piece valid in a hall) resolves the wrong-fixture finding. |  |  |  |
| 900 | move_piece | {"piece_id": "f_L-1_054", "snap_wall_id": "w_L-1_015", "offset": 0, "reason": "Snap the corner sofa's back onto the right exterior wall to fix F3 (back 1.10 m o | False | snap: f_L-1_054: no free place on wall w_L-1_015 (doors, windows, at most 0.3 m from the drawn place) | 0.0 -> 0.0 | adjusted_by_ai | Snap the corner sofa's back onto the right exterior wall to fix F3 (back 1.10 m off a wall) and clear the door-to-window walkway. |  | ![](images/r2_018_move_piece_before_r_L-1_salon_2.png) |  |
| 901 | move_piece | {"piece_id": "f_L-1_054", "center": [13.73, 3.27], "reason": "Shift the corner sofa 0.36 m right so its back sits on the right exterior wall (fixes F3) and it n | False | drawn_lock: f_L-1_054: a drawn piece moves at most 0.3 m (this move: 1.64 m) | 0.0 -> 0.0 | adjusted_by_ai | Shift the corner sofa 0.36 m right so its back sits on the right exterior wall (fixes F3) and it no longer blocks the door-to-window walkway (F6). |  | ![](images/r2_019_move_piece_before_r_L-1_salon_2.png) |  |
| 902 | move_piece | {"piece_id": "f_L-1_054", "center": [12.39, 3.27], "reason": "Nudge the corner sofa 0.30 m right toward the right wall to reduce the back-off-wall distance (F3) | False | f_L-1_054: clearance_ok, score: plausibility -58 -> -71 (F5 f_L-1_054: sofa_corner without a coffee table; F6 f_L-1_054: sofa_corner: the free zone in front of it is blocked by f_L-1_062) | 0.0 -> 0.0 | adjusted_by_ai | Nudge the corner sofa 0.30 m right toward the right wall to reduce the back-off-wall distance (F3) and ease the door-to-window walkway blockage (F6). |  | ![](images/r2_020_move_piece_before_r_L-1_salon_2.png) |  |
| 903 | move_piece | {"piece_id": "f_L-1_062", "center": [12.86, 2.87], "reason": "Nudge the small sofa 0.30 m toward the window wall so its back sits on the wall (fixes F3) and it  | False | drawn_lock: f_L-1_062: a drawn piece moves at most 0.3 m (this move: 0.30 m) | 0.0 -> 0.0 | adjusted_by_ai | Nudge the small sofa 0.30 m toward the window wall so its back sits on the wall (fixes F3) and it no longer blocks the corner sofa's free zone. |  | ![](images/r2_021_move_piece_before_r_L-1_salon_2.png) |  |
| 904 | move_piece | {"piece_id": "f_L-1_062", "center": [12.86, 2.88], "reason": "Nudge the small sofa 0.30 m toward the window wall so its back sits on the wall (fixes F3) and it  | True |  | 0.0 -> 0.0 | adjusted_by_ai | Nudge the small sofa 0.30 m toward the window wall so its back sits on the wall (fixes F3) and it no longer blocks the corner sofa's free zone. | refit | ![](images/r2_022_move_piece_before_r_L-1_salon_2.png) | ![](images/r2_023_move_piece_after_r_L-1_salon_2.png) |
| 905 | move_piece | {"piece_id": "f_L-1_054", "center": [12.39, 3.27], "reason": "Nudge the corner sofa 0.30 m right toward the right wall to reduce the back-off-wall distance (F3) | False | max_tries: f_L-1_054 was edited 3 times in this round |  | adjusted_by_ai | Nudge the corner sofa 0.30 m right toward the right wall to reduce the back-off-wall distance (F3) and ease the door-to-window walkway blockage (F6). |  |  |  |
| 906 | rotate_piece | {"piece_id": "f_L-1_050", "front_deg": 270, "reason": "Turn the armchair to face the sofa group (west) instead of the wall, fixing F4 and keeping its free zone  | True |  | 0.0 -> 0.0 | adjusted_by_ai | Turn the armchair to face the sofa group (west) instead of the wall, fixing F4 and keeping its free zone inside the room (F6). | refit | ![](images/r2_024_rotate_piece_before_r_L-1_salon_2.png) | ![](images/r2_025_rotate_piece_after_r_L-1_salon_2.png) |
| 907 | rotate_piece | {"piece_id": "f_L-1_103", "front_deg": 270, "reason": "Turn the AI armchair to face the sofa group (west) instead of the wall, fixing F4."} | True |  | 0.0 -> 0.0 | added_by_ai | Turn the AI armchair to face the sofa group (west) instead of the wall, fixing F4. | refit | ![](images/r2_026_rotate_piece_before_r_L-1_salon_2.png) | ![](images/r2_027_rotate_piece_after_r_L-1_salon_2.png) |
| 908 | move_piece | {"piece_id": "f_L-1_053", "snap_wall_id": "w_L-1_007", "offset": 2.5, "reason": "Snap the corner sofa's back to the west wall to fix F3 (back 1.10 m off a wall) | False | snap: f_L-1_053: no free place on wall w_L-1_007 (doors, windows, at most 0.3 m from the drawn place) | 0.0 -> 0.0 | adjusted_by_ai | Snap the corner sofa's back to the west wall to fix F3 (back 1.10 m off a wall) and clear the door-to-window walkway (F6). |  | ![](images/r2_029_move_piece_before_r_L-1_salon.png) |  |
| 909 | resize_piece | {"piece_id": "f_L-1_027", "size": [1.8, 0.9], "reason": "The drawn dining table is an oversized 3.35 m slab; resize to a real 1.8 m dining table matching the 8  | False | score: plausibility -28 -> -68 (F4 f_L-1_028: chair does not face its group (f_L-1_027); F4 f_L-1_031: chair does not face its group (f_L-1_027); F4 f_L-1_032: chair does not face its group (f_L-1_027); F4 f_L-1_035: chair does not face its group (f_L-1_027)) | 0.0 -> 0.0 | adjusted_by_ai | The drawn dining table is an oversized 3.35 m slab; resize to a real 1.8 m dining table matching the 8 chairs. |  | ![](images/r2_030_resize_piece_before_r_L-1_salon.png) |  |
| 910 | move_piece | {"piece_id": "f_L-1_063", "center": [4.3, 1.6], "reason": "Move the floor lamp away from the window (sill 0.90 m) to fix F7."} | False | drawn_lock: f_L-1_063: a drawn piece moves at most 0.3 m (this move: 0.86 m) | 0.0 -> 0.0 | adjusted_by_ai | Move the floor lamp away from the window (sill 0.90 m) to fix F7. |  | ![](images/r2_031_move_piece_before_r_L-1_salon.png) |  |
| 911 | move_piece | {"piece_id": "f_L-1_073", "center": [3.0, 1.9], "reason": "Move the coffee table in front of the sofa group so it is no longer standing alone (F8)."} | False | drawn_lock: f_L-1_073: a drawn piece moves at most 0.3 m (this move: 3.24 m) | 0.0 -> 0.0 | adjusted_by_ai | Move the coffee table in front of the sofa group so it is no longer standing alone (F8). |  | ![](images/r2_032_move_piece_before_r_L-1_salon.png) |  |
| 912 | move_piece | {"piece_id": "f_L-1_053", "center": [2.0, 3.27], "reason": "Shift the corner sofa west so its back sits on the west wall (fixes F3) and it no longer blocks the  | False | drawn_lock: f_L-1_053: a drawn piece moves at most 0.3 m (this move: 1.08 m) | 0.0 -> 0.0 | adjusted_by_ai | Shift the corner sofa west so its back sits on the west wall (fixes F3) and it no longer blocks the door-to-window walkway (F6). |  | ![](images/r2_033_move_piece_before_r_L-1_salon.png) |  |
| 913 | move_piece | {"piece_id": "f_L-1_063", "center": [4.3, 1.04], "reason": "Nudge the floor lamp 0.3 m away from the window sill to fix F7."} | False | f_L-1_053: no_overlap | 0.0 -> 0.0 | adjusted_by_ai | Nudge the floor lamp 0.3 m away from the window sill to fix F7. |  | ![](images/r2_034_move_piece_before_r_L-1_salon.png) |  |
| 914 | move_piece | {"piece_id": "f_L-1_073", "center": [5.82, 1.0], "reason": "Nudge the coffee table 0.3 m toward the seating group to reduce its isolation (F8)."} | False | f_L-1_073: no_overlap, f_L-1_077: no_overlap | 0.0 -> 0.0 | adjusted_by_ai | Nudge the coffee table 0.3 m toward the seating group to reduce its isolation (F8). |  | ![](images/r2_035_move_piece_before_r_L-1_salon.png) |  |
| 915 | remove_piece | {"piece_id": "f_L-1b_001", "reason": "5.54x2.77 m unknown box in the room centre is not furniture; the plan crop shows no such object there, it is a misread hat | False | no_change: f_L-1b_001 is not built already | 55.0 -> 55.0 | adjusted_by_ai | 5.54x2.77 m unknown box in the room centre is not furniture; the plan crop shows no such object there, it is a misread hatch/outline that collides with the island and stools. |  | ![](images/r2_037_remove_piece_before_r_L-1b_acik_mutfak_2.png) |  |
| 916 | remove_piece | {"piece_id": "f_L-1b_039", "reason": "Second unexplained 2.13x0.9 m box in the room centre; the plan crop shows no such object, it is a misread outline overlapp | False | drawn_lock: f_L-1b_039: drawn fixed equipment (kitchen_island) is never removed | 55.0 -> 55.0 | adjusted_by_ai | Second unexplained 2.13x0.9 m box in the room centre; the plan crop shows no such object, it is a misread outline overlapping the real island and stools. |  | ![](images/r2_038_remove_piece_before_r_L-1b_acik_mutfak_2.png) |  |
| 917 | remove_piece | {"piece_id": "f_L-1b_043", "reason": "1.34 m² unknown box at the room's left edge; the plan crop shows no furniture there, it is a misread outline."} | True |  | 55.0 -> 65.0 | adjusted_by_ai | 1.34 m² unknown box at the room's left edge; the plan crop shows no furniture there, it is a misread outline. | refit | ![](images/r2_039_remove_piece_before_r_L-1b_acik_mutfak_2.png) | ![](images/r2_040_remove_piece_after_r_L-1b_acik_mutfak_2.png) |
| 918 | move_piece | {"piece_id": "f_L-1b_007", "center": [13.9976, 6.75], "reason": "Shift the stove 0.27 m off the counter line so it no longer overlaps kitchen_counter f_L-1b_003 | False | drawn_lock: f_L-1b_007: drawn fixed equipment (stove) is never moved | 65.0 -> 65.0 | adjusted_by_ai | Shift the stove 0.27 m off the counter line so it no longer overlaps kitchen_counter f_L-1b_003. |  | ![](images/r2_041_move_piece_before_r_L-1b_acik_mutfak_2.png) |  |
| 919 | move_piece | {"piece_id": "f_L-1b_053", "center": [14.6692, 5.15], "reason": "Shift the fridge 0.73 m along the right wall so it no longer overlaps kitchen_counter f_L-1b_00 | False | drawn_lock: f_L-1b_053: drawn fixed equipment (fridge) is never moved | 65.0 -> 65.0 | adjusted_by_ai | Shift the fridge 0.73 m along the right wall so it no longer overlaps kitchen_counter f_L-1b_004. |  | ![](images/r2_042_move_piece_before_r_L-1b_acik_mutfak_2.png) |  |
| 920 | move_piece | {"piece_id": "f_L-1b_076", "center": [8.1, 6.9], "reason": "Move the AI tall cabinet from the middle of the room to the left wall so it no longer blocks the wal | False | f_L-1b_076: inside_room | 65.0 -> 65.0 | added_by_ai | Move the AI tall cabinet from the middle of the room to the left wall so it no longer blocks the walkway between island and dining area. |  | ![](images/r2_043_move_piece_before_r_L-1b_acik_mutfak_2.png) |  |
| 921 | remove_piece | {"piece_id": "f_L1_003", "reason": "The plan crop shows f_L1_003 is a dashed outline enclosing the two drawn sofas and a rug circle — it is a grouping/rug bound | False | no_change: f_L1_003 is not built already | 22.0 -> 22.0 | adjusted_by_ai | The plan crop shows f_L1_003 is a dashed outline enclosing the two drawn sofas and a rug circle — it is a grouping/rug boundary, not a solid furniture piece, so it must not be built as an opaque block. |  | ![](images/r2_045_remove_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |  |
| 922 | change_type | {"piece_id": "f_L1_005", "type": "bench", "reason": "The plan crop shows f_L1_005 as a long thin 3.66×0.4 m drawn strip along the top wall — a low bench/seat, n | False | room_type: bench is not a piece a other room may hold here | 22.0 -> 22.0 | adjusted_by_ai | The plan crop shows f_L1_005 as a long thin 3.66×0.4 m drawn strip along the top wall — a low bench/seat, not an unknown box. |  | ![](images/r2_046_change_type_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |  |
| 923 | change_type | {"piece_id": "f_L1_005", "type": "console_table", "reason": "The plan crop shows f_L1_005 as a long thin 3.66×0.4 m drawn strip along the top wall — a low conso | False | room_type: console_table is not a piece a other room may hold here | 22.0 -> 22.0 | adjusted_by_ai | The plan crop shows f_L1_005 as a long thin 3.66×0.4 m drawn strip along the top wall — a low console/bench seat, not an unknown box. |  | ![](images/r2_047_change_type_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |  |
| 924 | change_type | {"piece_id": "f_L1_017", "type": "table_coffee", "reason": "The plan crop shows f_L1_017 as a ~1.6×1.5 m square table with a circular rug drawn around it in the | False | room_type: table_coffee is not a piece a other room may hold here | 22.0 -> 22.0 | adjusted_by_ai | The plan crop shows f_L1_017 as a ~1.6×1.5 m square table with a circular rug drawn around it in the lounge corner — a coffee/activity table, not an unknown box. |  | ![](images/r2_048_change_type_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |  |
| 925 | set_room_type | {"room_id": "r_L1_oyun_aktivite_ve_dinlenme_odasi", "room_type": "living", "reason": "The room is a 40 m² lounge with two drawn sofas, an ottoman and a coffee t | True |  | 22.0 -> 25.0 | adjusted_by_ai | The room is a 40 m² lounge with two drawn sofas, an ottoman and a coffee table — a living room, so its furniture (sofas, tables) is valid and the F1/F9 checks resolve. | layout | ![](images/r2_049_set_room_type_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) | ![](images/r2_050_set_room_type_after_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |
| 926 | change_type | {"piece_id": "f_L1_005", "type": "bench", "reason": "The plan crop shows f_L1_005 as a long thin 3.66×0.4 m drawn strip along the top wall — a low bench/seat, n | False | room_type: bench is not a piece a living room may hold here | 25.0 -> 25.0 | adjusted_by_ai | The plan crop shows f_L1_005 as a long thin 3.66×0.4 m drawn strip along the top wall — a low bench/seat, not an unknown box. |  | ![](images/r2_051_change_type_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |  |
| 927 | change_type | {"piece_id": "f_L1_017", "type": "table_coffee", "reason": "The plan crop shows f_L1_017 as a ~1.6×1.5 m square table with a circular rug drawn around it in the | False | product_size: f_L1_017: 1.63 x 1.52 m does not fit a table_coffee (size table) | 25.0 -> 25.0 | adjusted_by_ai | The plan crop shows f_L1_017 as a ~1.6×1.5 m square table with a circular rug drawn around it in the lounge corner — a coffee/activity table, not an unknown box. |  | ![](images/r2_052_change_type_before_r_L1_oyun_aktivite_ve_dinlenme_odasi.png) |  |
| 928 | move_piece | {"piece_id": "f_L1_010", "snap_wall_id": "w_L1_015", "offset": 1.5, "reason": "Snap the sofa's back onto the right wall (w_L1_015) to fix F3 (back 2.48 m off a  | False | snap: f_L1_010: no free place on wall w_L1_015 (doors, windows, at most 0.3 m from the drawn place) | 22.0 -> 22.0 | adjusted_by_ai | Snap the sofa's back onto the right wall (w_L1_015) to fix F3 (back 2.48 m off a wall). |  | ![](images/r2_054_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |  |
| 929 | move_piece | {"piece_id": "f_L1_011", "snap_wall_id": "w_L1_012", "offset": 5.5, "reason": "Snap the sofa's back onto the left wall (w_L1_012) to fix F3 (back 0.79 m off a w | False | snap: f_L1_011: no free place on wall w_L1_012 (doors, windows, at most 0.3 m from the drawn place) | 22.0 -> 22.0 | adjusted_by_ai | Snap the sofa's back onto the left wall (w_L1_012) to fix F3 (back 0.79 m off a wall). |  | ![](images/r2_055_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |  |
| 930 | move_piece | {"piece_id": "f_L1_010", "center": [12.92, 4.02], "reason": "Move the sofa so its back sits on the right wall (w_L1_015) to fix F3 (back 2.48 m off a wall)."} | False | drawn_lock: f_L1_010: a drawn piece moves at most 0.3 m (this move: 1.96 m) | 22.0 -> 22.0 | adjusted_by_ai | Move the sofa so its back sits on the right wall (w_L1_015) to fix F3 (back 2.48 m off a wall). |  | ![](images/r2_056_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |  |
| 931 | move_piece | {"piece_id": "f_L1_011", "center": [8.24, 5.91], "reason": "Move the sofa so its back sits on the left wall (w_L1_012) to fix F3 (back 0.79 m off a wall)."} | False | drawn_lock: f_L1_011: a drawn piece moves at most 0.3 m (this move: 1.28 m) | 22.0 -> 22.0 | adjusted_by_ai | Move the sofa so its back sits on the left wall (w_L1_012) to fix F3 (back 0.79 m off a wall). |  | ![](images/r2_057_move_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |  |
| 932 | remove_piece | {"piece_id": "f_L1_004", "reason": "The 13.56 m² box is a dashed hatch/zone outline (activity area) drawn behind the sofas, not furniture; remove it to resolve  | False | no_change: f_L1_004 is not built already | 22.0 -> 22.0 | adjusted_by_ai | The 13.56 m² box is a dashed hatch/zone outline (activity area) drawn behind the sofas, not furniture; remove it to resolve F9. |  | ![](images/r2_058_remove_piece_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |  |
| 933 | change_type | {"piece_id": "f_L1_018", "type": "table_coffee", "reason": "The 1.63×1.52 m drawn box in the play area is a low activity table; change from unknown to table_cof | False | room_type: table_coffee is not a piece a other room may hold here | 22.0 -> 22.0 | adjusted_by_ai | The 1.63×1.52 m drawn box in the play area is a low activity table; change from unknown to table_coffee to resolve F9. |  | ![](images/r2_059_change_type_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |  |
| 934 | change_type | {"piece_id": "f_L1_006", "type": "bench", "reason": "The 3.66×0.4 m drawn strip along the top is a low bench; change from unknown to bench to resolve F9."} | False | room_type: bench is not a piece a other room may hold here | 22.0 -> 22.0 | adjusted_by_ai | The 3.66×0.4 m drawn strip along the top is a low bench; change from unknown to bench to resolve F9. |  | ![](images/r2_060_change_type_before_r_L1_oyun_aktivite_ve_dinlenme_odasi_2.png) |  |
| 935 | move_piece | {"piece_id": "f_L-1_008", "snap_wall_id": "w_L-1_002", "offset": 1.3832, "reason": "Snap stove back onto the north wall to fix the 0.06 m off-wall gap and the o | False | drawn_lock: f_L-1_008: drawn fixed equipment (stove) is never moved | 48.0 -> 48.0 | adjusted_by_ai | Snap stove back onto the north wall to fix the 0.06 m off-wall gap and the overlap with counter f_L-1_002. |  | ![](images/r2_062_move_piece_before_r_L-1_mutfak.png) |  |
| 936 | move_piece | {"piece_id": "f_L-1_067", "snap_wall_id": "w_L-1_007", "offset": 1, "reason": "Test whether the drawn fridge can be repositioned along the west wall away from t | False | drawn_lock: f_L-1_067: drawn fixed equipment (fridge) is never moved | 48.0 -> 48.0 | adjusted_by_ai | Test whether the drawn fridge can be repositioned along the west wall away from the window. |  | ![](images/r2_063_move_piece_before_r_L-1_mutfak.png) |  |
| 937 | remove_piece | {"piece_id": "f_L-1_006", "reason": "Plan crop shows f_L-1_006 is a small drawn detail (0.10 m²) inside the kitchen counter run, not a separate piece of furnitu | True |  | 48.0 -> 51.0 | adjusted_by_ai | Plan crop shows f_L-1_006 is a small drawn detail (0.10 m²) inside the kitchen counter run, not a separate piece of furniture. | refit | ![](images/r2_064_remove_piece_before_r_L-1_mutfak.png) | ![](images/r2_065_remove_piece_after_r_L-1_mutfak.png) |
| 938 | remove_piece | {"piece_id": "f_L-1_007", "reason": "Plan crop shows f_L-1_007 is a small drawn detail (0.10 m²) inside the kitchen counter run, not a separate piece of furnitu | True |  | 51.0 -> 54.0 | adjusted_by_ai | Plan crop shows f_L-1_007 is a small drawn detail (0.10 m²) inside the kitchen counter run, not a separate piece of furniture. | refit | ![](images/r2_066_remove_piece_before_r_L-1_mutfak.png) | ![](images/r2_067_remove_piece_after_r_L-1_mutfak.png) |
| 939 | swap_model | {"piece_id": "f_L-1_094", "asset_id": "tall_cabinet_02", "reason": "Replace the featureless white block tall cabinet with a detailed library model so it reads a | False | asset_exists: no catalogue model 'tall_cabinet_02' | 54.0 -> 54.0 | added_by_ai | Replace the featureless white block tall cabinet with a detailed library model so it reads as finished furniture. |  | ![](images/r2_068_swap_model_before_r_L-1_mutfak.png) |  |

Re-runs and renders:

| seq | kind | from | status | views | seconds | before | after | note |
|---|---|---|---|---|---|---|---|---|
| 940 | rerun | layout | failed | cam_r_L-1_mutfak_1, cam_r_L-1_mutfak_2, cam_r_L-1_mutfak_3, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2, cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 | 15.6 |  |  | refit refused the round's edits: 7 edit(s) rolled back |
| 941 | render |  | preview | cam_r_L-1_mutfak_1 |  | ![](images/r2_cam_r_L-1_mutfak_1_before.jpg) | ![](images/r2_cam_r_L-1_mutfak_1_after.jpg) |  |
| 942 | render |  | preview | cam_r_L-1_mutfak_2 |  | ![](images/r2_cam_r_L-1_mutfak_2_before.jpg) | ![](images/r2_cam_r_L-1_mutfak_2_after.jpg) |  |
| 943 | render |  | preview | cam_r_L-1_mutfak_3 |  | ![](images/r2_cam_r_L-1_mutfak_3_before.jpg) | ![](images/r2_cam_r_L-1_mutfak_3_after.jpg) |  |
| 944 | render |  | preview | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1 |  | ![](images/r2_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_before.jpg) | ![](images/r2_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_1_after.jpg) |  |
| 945 | render |  | preview | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2 |  | ![](images/r2_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_before.jpg) | ![](images/r2_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_2_after.jpg) |  |
| 946 | render |  | preview | cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3 |  | ![](images/r2_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_before.jpg) | ![](images/r2_cam_r_L1_oyun_aktivite_ve_dinlenme_odasi_3_after.jpg) |  |

Stop: the re-run of the changed stages failed (11 edits accepted in 2 rounds)

## Round 3

Findings: 0 (0 dropped).

Stop: time budget: the final stages need the time left before the deadline - 20 min (final round for critical findings not started)
