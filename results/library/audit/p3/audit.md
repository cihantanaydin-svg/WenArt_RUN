# Library audit

## Totals

| status | models |
|---|---|
| keep | 649 |
| keep? | 2 |
| fix | 166 |
| removed | 249 |

## Per source

| source | keep | keep? | fix | removed | total |
|---|---|---|---|---|---|
| abo | 388 | 0 | 87 | 63 | 538 |
| generated | 138 | 2 | 58 | 83 | 281 |
| objaverse | 99 | 0 | 15 | 99 | 213 |
| polyhaven | 24 | 0 | 6 | 4 | 34 |

## Per type

| kind | type | keep | keep? | fix | removed | total |
|---|---|---|---|---|---|---|
| furniture | bed_single | 7 | 0 | 6 | 7 | 20 |
| furniture | bed_double | 16 | 0 | 2 | 3 | 21 |
| furniture | sofa | 17 | 0 | 0 | 6 | 23 |
| furniture | armchair | 23 | 0 | 0 | 0 | 23 |
| furniture | table_dining | 16 | 0 | 0 | 7 | 23 |
| furniture | table_coffee | 21 | 0 | 0 | 2 | 23 |
| furniture | desk | 17 | 0 | 4 | 2 | 23 |
| furniture | chair | 8 | 0 | 9 | 5 | 22 |
| furniture | wardrobe | 7 | 0 | 9 | 4 | 20 |
| furniture | fridge | 1 | 0 | 6 | 12 | 19 |
| furniture | stove | 13 | 0 | 1 | 6 | 20 |
| furniture | sink_kitchen | 5 | 0 | 0 | 10 | 15 |
| furniture | washbasin | 13 | 0 | 0 | 7 | 20 |
| furniture | toilet | 0 | 0 | 7 | 12 | 19 |
| furniture | shower | 7 | 0 | 0 | 3 | 10 |
| furniture | bathtub | 5 | 0 | 0 | 15 | 20 |
| furniture | tv_unit | 19 | 0 | 1 | 2 | 22 |
| furniture | bookshelf | 12 | 0 | 9 | 2 | 23 |
| furniture | nightstand | 6 | 0 | 15 | 0 | 21 |
| furniture | dresser | 3 | 0 | 16 | 1 | 20 |
| furniture | washing_machine | 0 | 0 | 16 | 4 | 20 |
| furniture | side_table | 17 | 0 | 0 | 3 | 20 |
| furniture | floor_lamp | 13 | 0 | 0 | 7 | 20 |
| furniture | potted_plant | 16 | 0 | 0 | 4 | 20 |
| furniture | sofa_corner | 16 | 0 | 2 | 1 | 19 |
| furniture | chaise | 4 | 0 | 5 | 1 | 10 |
| furniture | ottoman | 18 | 0 | 0 | 2 | 20 |
| furniture | bench | 13 | 0 | 0 | 7 | 20 |
| furniture | bar_stool | 18 | 0 | 2 | 0 | 20 |
| furniture | office_chair | 5 | 0 | 13 | 2 | 20 |
| furniture | console_table | 20 | 0 | 0 | 0 | 20 |
| furniture | crib | 3 | 0 | 2 | 3 | 8 |
| furniture | bunk_bed | 0 | 0 | 6 | 4 | 10 |
| furniture | sideboard | 14 | 0 | 6 | 0 | 20 |
| furniture | shoe_cabinet | 8 | 0 | 12 | 0 | 20 |
| furniture | display_cabinet | 2 | 0 | 5 | 1 | 8 |
| furniture | tall_cabinet | 1 | 0 | 11 | 5 | 17 |
| decor | cushion | 17 | 0 | 0 | 4 | 21 |
| decor | rug | 20 | 0 | 0 | 0 | 20 |
| decor | wall_art | 10 | 0 | 0 | 7 | 17 |
| decor | vase | 20 | 0 | 0 | 0 | 20 |
| decor | bowl | 17 | 2 | 0 | 0 | 19 |
| decor | plant_small | 20 | 0 | 0 | 0 | 20 |
| decor | table_lamp | 19 | 0 | 0 | 1 | 20 |
| decor | mirror | 9 | 0 | 0 | 8 | 17 |
| decor | curtain | 14 | 0 | 0 | 6 | 20 |
| decor | blind | 5 | 0 | 0 | 4 | 9 |
| decor | throw | 6 | 0 | 0 | 11 | 17 |
| decor | books | 12 | 0 | 0 | 8 | 20 |
| decor | candle | 15 | 0 | 0 | 5 | 20 |
| decor | basket | 16 | 0 | 0 | 4 | 20 |
| decor | tray | 7 | 0 | 1 | 12 | 20 |
| decor | clock | 8 | 0 | 0 | 12 | 20 |
| decor | sculpture | 12 | 0 | 0 | 5 | 17 |
| decor | plant_large | 9 | 0 | 0 | 1 | 10 |
| decor | pendant_light | 15 | 0 | 0 | 5 | 20 |
| decor | ceiling_light | 11 | 0 | 0 | 6 | 17 |
| decor | plant | 3 | 0 | 0 | 0 | 3 |

## Removal reasons (a model may have several)

| reason | models |
|---|---|
| vision check | 240 |
| title flag | 32 |
| title names another type | 31 |
| proportions fit no real piece | 28 |
| licence not allowed | 18 |
| few faces (crude unless the vision quality is high) | 14 |
| a drawer, door or lid is open, or a part floats ap | 10 |
| duplicate | 3 |

## Fixes (catalogue fields)

| fix | models |
|---|---|
| front_quarter_turns | 162 |
| rescale | 6 |
| type | 1 |

## Waiting for the vision check

| needs | models |
|---|---|
| vision pass 2: no title evidence | 2 |

## Models to remove (catalogue only; the files stay on the volume)

| id | type | source | status | reason | title |
|---|---|---|---|---|---|
| gen_bed_single_classic_1_dbac0f10 | bed_single | generated | removed | proportions 1.19 x 1.68 x 1.08 m fit no real bed_single (width (0.8, 1.2), depth (1.8, 2.2), height (0.25, 1.6)) | Generated classic bed single (1) |
| gen_bed_single_japandi_1_35dff430 | bed_single | generated | removed | proportions 1.26 x 1.59 x 0.67 m fit no real bed_single (width (0.8, 1.2), depth (1.8, 2.2), height (0.25, 1.6)) | Generated japandi bed single (1) |
| gen_bed_single_mediterranean_1_c9d313b4 | bed_single | generated | removed | proportions 1.21 x 1.65 x 0.86 m fit no real bed_single (width (0.8, 1.2), depth (1.8, 2.2), height (0.25, 1.6)) | Generated mediterranean bed single (1) |
| gen_bed_single_mediterranean_2_8f745c9f | bed_single | generated | removed | the vision check sees more than one object | Generated mediterranean bed single (2) |
| gen_bed_single_modern_minimal_1_5c05505b | bed_single | generated | removed | proportions 1.29 x 1.57 x 0.75 m fit no real bed_single (width (0.8, 1.2), depth (1.8, 2.2), height (0.25, 1.6)) | Generated modern minimal bed single (1) |
| gen_bed_single_scandinavian_1_8060783a | bed_single | generated | removed | proportions 1.24 x 1.62 x 0.72 m fit no real bed_single (width (0.8, 1.2), depth (1.8, 2.2), height (0.25, 1.6)) | Generated scandinavian bed single (1) |
| objaverse_6eb4212e70b941a3bd2db196a47828b9 | bed_single | objaverse | removed | the title says lowpoly: not photoreal | Lowpoly Bed |
| abo_B01N6AQX0A | bed_double | abo | removed | the title says luchtbed: not the object | Intex Premaire Luchtbed met Fiber Tech-technologie, nieuwe g |
| abo_B084ZBDPG5 | bed_double | abo | removed | vision quality 2 (<= 2) | Amazon Brand – Stone & Beam Rustic Solid Pine Bed with Headb |
| abo_B084ZBX1YH | bed_double | abo | removed | vision quality 2 (<= 2) | Amazon Brand – Stone & Beam Rustic Solid Pine Platform Bed,  |
| abo_B07HZ5P7P9 | sofa | abo | removed | the title says sectional component: a part of a piece | Amazon Brand – Stone & Beam Bagley Sectional Component, Left |
| abo_B07HZ6GJC2 | sofa | abo | removed | the title says sectional component: a part of a piece | Amazon Brand – Stone & Beam Bagley Sectional Component, Righ |
| abo_B07HZ6HHFF | sofa | abo | removed | the title says sectional component: a part of a piece | Amazon Brand – Stone & Beam Bagley Sectional Component, Arml |
| abo_B07HZ6X7ZF | sofa | abo | removed | the title says sectional component: a part of a piece | Amazon Brand – Stone & Beam Bagley Sectional Component, Left |
| abo_B07HZ72L2H | sofa | abo | removed | the title says sectional component: a part of a piece | Amazon Brand – Stone & Beam Bagley Sectional Component, Righ |
| gen_sofa_japandi_2_98a7a89b | sofa | generated | removed | the vision check sees more than one object | Generated japandi sofa (2) |
| abo_B07B82WF6G | table_dining | abo | removed | the vision check says it is not a table_dining (a table_coffee) | Amazon Brand – Rivet Mid-Century Modern Wood Round Dining Ki |
| abo_B07H8SZNZF | table_dining | abo | removed | the vision check says it is not a table_dining (a table_coffee) | Movian Moselle Dining Table, 160 x 76 x 90cm, Oak Sonoma Col |
| abo_B07M6PKC6B | table_dining | abo | removed | the vision check says it is not a table_dining (a side_table) | Amazon Brand – Ravenna Home Traditional Dining Table 29"H, G |
| abo_B07ML7P94G | table_dining | abo | removed | the vision check says it is not a table_dining (a side_table) | Amazon Brand – Ravenna Home Traditional Dining Table 29"H, B |
| objaverse_3b4ee19c627e4fb4a3305621cf925aa2 | table_dining | objaverse | removed | the title says dining set: several objects (a set or a scene) (the vision check confirms) | Dining Set |
| objaverse_724d93a7f3644f96909e8c55909c6418 | table_dining | objaverse | removed | the title says table chairs: several objects (a set or a scene) (the vision check confirms) | A table, chairs & few cups |
| abo_B072ZK2FZ6 | table_coffee | abo | removed | proportions 0.80 x 0.36 x 0.58 m fit no real table_coffee (width (0.6, 1.4), depth (0.4, 1.2), height (0.25, 0.6)) | Amazon Brand – Rivet Industrial Modern Wood and Metal Coffee |
| objaverse_bbe1d47c0d714884a66c53d6c1e5d177 | table_coffee | objaverse | removed | the title names mesa comedor, not a table_coffee | MESA COMEDOR |
| objaverse_1b256f6ce7924f59a756fe8f7ba69416 | desk | objaverse | removed | the title says test: not photoreal | FF Desk Drawer 3D Test 5 Obj |
| abo_B01MQJV7ID | chair | abo | removed | the vision check says it is not a chair (a office_chair) | AmazonBasics Sedia direzionale da ufficio con schienale alto |
| abo_B07DBD9WHX | chair | abo | removed | the vision check says it is not a chair (a armchair) | Amazon Brand – Ravenna Home Armless Tufted Turned Wood Leg A |
| abo_B07JK8CL2Z | chair | abo | removed | the vision check says it is not a chair (a armchair) | Amazon Brand - Movian Square |
| objaverse_cb43e2abac66494d81e1e7116eb47043 | chair | objaverse | removed | 2560 triangles (< 3000): crude unless the vision quality is high; vision quality 3 | Vintage Chair |
| abo_B07GFRKNR1 | wardrobe | abo | removed | the vision check says it is not a wardrobe (a tall_cabinet) | Amazon Brand - Movian Inari Modern 2-Door 2-Drawer Wardrobe, |
| objaverse_05a035c3347645b8a7ceb6d65f825ac3 | wardrobe | objaverse | removed | a drawer, door or lid is open, or a part floats apart | Dikkies Closet |
| objaverse_094697a23146463cb5564ac8bf89e5c4 | wardrobe | objaverse | removed | licence CC-BY-NC-4.0 not allowed (user decision of 10 Oct 2026) | Traditional Mennonite corner cabinet |
| objaverse_b46803ba0bc64e12b31f832fb761c4e0 | wardrobe | objaverse | removed | the title names shelf, not a wardrobe | Simple Tall Shelf |
| gen_fridge_industrial_3_029d56da | fridge | generated | removed | the vision check sees more than one object | Generated industrial fridge (3) |
| gen_fridge_japandi_1_4c9cd582 | fridge | generated | removed | vision quality 2 (<= 2) | Generated japandi fridge (1) |
| gen_fridge_japandi_2_4c7dbc82 | fridge | generated | removed | the vision check sees more than one object | Generated japandi fridge (2) |
| gen_fridge_japandi_3_38a9d0f8 | fridge | generated | removed | vision quality 2 (<= 2) | Generated japandi fridge (3) |
| gen_fridge_modern_minimal_1_c27ed7d7 | fridge | generated | removed | vision quality 2 (<= 2) | Generated modern minimal fridge (1) |
| gen_fridge_rustic_1_06be6df4 | fridge | generated | removed | the vision check sees more than one object | Generated rustic fridge (1) |
| gen_fridge_scandinavian_1_315b4d87 | fridge | generated | removed | the vision check sees more than one object | Generated scandinavian fridge (1) |
| gen_fridge_scandinavian_6_87b23e5c | fridge | generated | removed | vision quality 2 (<= 2) | Generated scandinavian fridge (6) |
| objaverse_2071bda681b642218b6829b82e4fd93b | fridge | objaverse | removed | 2096 triangles (< 3000): crude unless the vision quality is high; vision quality 3 | Refrigerator - Grey Polished Metal |
| objaverse_68d69bbf7a454a09a2536ac0762532f3 | fridge | objaverse | removed | 2074 triangles (< 3000): crude unless the vision quality is high; vision quality 3 | Old Fridge |
| objaverse_c9c4e705bf794cb88d5d8726095f4917 | fridge | objaverse | removed | licence CC-BY-NC-4.0 not allowed (user decision of 10 Oct 2026) | Haier Refrigerator |
| objaverse_f32ec9229a8749d1b79245813fbd6c31 | fridge | objaverse | removed | the title says stylized: not photoreal | Stylized Fridge |
| gen_stove_japandi_6_1c3993c0 | stove | generated | removed | the vision check sees more than one object | Generated japandi stove (6) |
| gen_stove_modern_minimal_1_18c4c83a | stove | generated | removed | proportions 0.94 x 0.77 x 0.80 m fit no real stove (width (0.45, 0.95), depth (0.5, 0.7), height (0.8, 1.2)) | Generated modern minimal stove (1) |
| gen_stove_scandinavian_2_4aebb9bc | stove | generated | removed | proportions 1.00 x 0.80 x 0.80 m fit no real stove (width (0.45, 0.95), depth (0.5, 0.7), height (0.8, 1.2)) | Generated scandinavian stove (2) |
| gen_stove_scandinavian_4_c71c9213 | stove | generated | removed | proportions 1.03 x 0.73 x 0.80 m fit no real stove (width (0.45, 0.95), depth (0.5, 0.7), height (0.8, 1.2)) | Generated scandinavian stove (4) |
| objaverse_68e164f1a9414c29820ac2eaf6d8ac04 | stove | objaverse | removed | vision quality 2 (<= 2) | Stove from Poly by Google |
| objaverse_934716ccd00d4f6ba9555d1cea788488 | stove | objaverse | removed | vision quality 2 (<= 2) | R RETRO FIRIN |
| gen_sink_kitchen_industrial_4_3f68e743 | sink_kitchen | generated | removed | vision quality 2 (<= 2) | Generated industrial sink kitchen (4) |
| gen_sink_kitchen_japandi_2_d6ae0419 | sink_kitchen | generated | removed | vision quality 2 (<= 2) | Generated japandi sink kitchen (2) |
| gen_sink_kitchen_japandi_4_329115ec | sink_kitchen | generated | removed | vision quality 2 (<= 2) | Generated japandi sink kitchen (4) |
| gen_sink_kitchen_mediterranean_1_ae36322f | sink_kitchen | generated | removed | vision quality 2 (<= 2) | Generated mediterranean sink kitchen (1) |
| gen_sink_kitchen_mediterranean_3_f6d72c7b | sink_kitchen | generated | removed | vision quality 2 (<= 2) | Generated mediterranean sink kitchen (3) |
| gen_sink_kitchen_modern_1_5b97156d | sink_kitchen | generated | removed | vision quality 2 (<= 2) | Generated modern sink kitchen (1) |
| gen_sink_kitchen_modern_2_b348b4dc | sink_kitchen | generated | removed | vision quality 2 (<= 2) | Generated modern sink kitchen (2) |
| gen_sink_kitchen_modern_5_5f86535a | sink_kitchen | generated | removed | vision quality 2 (<= 2) | Generated modern sink kitchen (5) |
| gen_sink_kitchen_scandinavian_1_dbad65c6 | sink_kitchen | generated | removed | vision quality 2 (<= 2) | Generated scandinavian sink kitchen (1) |
| gen_sink_kitchen_scandinavian_3_3e309f4c | sink_kitchen | generated | removed | vision quality 2 (<= 2) | Generated scandinavian sink kitchen (3) |
| gen_washbasin_mediterranean_1_93c90025 | washbasin | generated | removed | vision quality 2 (<= 2) | Generated mediterranean washbasin (1) |
| gen_washbasin_mediterranean_4_c5dc64de | washbasin | generated | removed | the vision check sees more than one object | Generated mediterranean washbasin (4) |
| gen_washbasin_rustic_1_2d54af97 | washbasin | generated | removed | vision quality 2 (<= 2) | Generated rustic washbasin (1) |
| gen_washbasin_scandinavian_1_6efd9d50 | washbasin | generated | removed | the vision check sees more than one object | Generated scandinavian washbasin (1) |
| objaverse_3eafb89804b54c8e8cbe35e4d456e0a9 | washbasin | objaverse | removed | licence CC-BY-SA-4.0 not allowed (user decision of 10 Oct 2026) | Bathroom |
| objaverse_493b70a6177d4a1385b6b0ce041a93b0 | washbasin | objaverse | removed | 1070 triangles (< 3000): crude unless the vision quality is high; vision quality 3 | same sink but less sanitary |
| objaverse_f76c502218884914a27148f656a9b656 | washbasin | objaverse | removed | the title names bathroom, not a washbasin | Bathroom1 |
| gen_toilet_industrial_1_3cd5bde9 | toilet | generated | removed | vision quality 2 (<= 2) | Generated industrial toilet (1) |
| gen_toilet_japandi_1_42fdb46f | toilet | generated | removed | vision quality 2 (<= 2) | Generated japandi toilet (1) |
| gen_toilet_minimal_1_3799392b | toilet | generated | removed | the vision check sees more than one object | Generated minimal toilet (1) |
| gen_toilet_rustic_1_c2ce66a1 | toilet | generated | removed | the vision check sees more than one object | Generated rustic toilet (1) |
| objaverse_0b3325fad3e740b1ac86173c90b56afd | toilet | objaverse | removed | a drawer, door or lid is open, or a part floats apart | Toilettes |
| objaverse_1bd73c9a74d14ce29e45c277570990e6 | toilet | objaverse | removed | licence CC-BY-SA-4.0 not allowed (user decision of 10 Oct 2026) | Zenit Close Coupled Push Button Flush Toilet |
| objaverse_24d1b493899d407780140688abae19bc | toilet | objaverse | removed | a drawer, door or lid is open, or a part floats apart | Toilet |
| objaverse_3446229dce1f47528fa871cc7669136c | toilet | objaverse | removed | vision quality 2 (<= 2) | Toilet |
| objaverse_4398bcb5976945b08f195816340247b8 | toilet | objaverse | removed | licence CC-BY-SA-4.0 not allowed (user decision of 10 Oct 2026) | Memoirs Stately Close Coupled Toilet |
| objaverse_5b18711616054a44b025d9272b745a6a | toilet | objaverse | removed | the title says low poly: not photoreal | Qualitas Bathrooms toilet low poly |
| objaverse_bd0f8d2bfba24376bec2b827a0cbbabe | toilet | objaverse | removed | licence CC-BY-NC-4.0 not allowed (user decision of 10 Oct 2026) | CWLCCST1-6DT01 Ld |
| objaverse_c901dfa120a0487a9f5c9a2d241f70ab | toilet | objaverse | removed | the title says low poly: not photoreal | Animated low poly toilet |
| gen_shower_japandi_9_4f1cedc6 | shower | generated | removed | vision quality 2 (<= 2) | Generated japandi shower (9) |
| gen_shower_minimal_1_25eeb7e2 | shower | generated | removed | vision quality 2 (<= 2) | Generated minimal shower (1) |
| gen_shower_modern_minimal_6_664da6f5 | shower | generated | removed | vision quality 2 (<= 2) | Generated modern minimal shower (6) |
| gen_bathtub_classic_3_f7c924e0 | bathtub | generated | removed | proportions 1.43 x 0.81 x 0.80 m fit no real bathtub (width (1.4, 1.9), depth (0.65, 0.9), height (0.4, 0.72)) | Generated classic bathtub (3) |
| gen_bathtub_japandi_3_83eb18c0 | bathtub | generated | removed | proportions 1.45 x 0.84 x 0.80 m fit no real bathtub (width (1.4, 1.9), depth (0.65, 0.9), height (0.4, 0.72)) | Generated japandi bathtub (3) |
| gen_bathtub_mediterranean_1_11d9dbc8 | bathtub | generated | removed | proportions 1.32 x 0.78 x 0.80 m fit no real bathtub (width (1.4, 1.9), depth (0.65, 0.9), height (0.4, 0.72)) | Generated mediterranean bathtub (1) |
| gen_bathtub_modern_1_009871cf | bathtub | generated | removed | proportions 1.33 x 0.80 x 0.80 m fit no real bathtub (width (1.4, 1.9), depth (0.65, 0.9), height (0.4, 0.72)) | Generated modern bathtub (1) |
| gen_bathtub_modern_5_e14ba0b4 | bathtub | generated | removed | proportions 1.43 x 0.74 x 0.80 m fit no real bathtub (width (1.4, 1.9), depth (0.65, 0.9), height (0.4, 0.72)) | Generated modern bathtub (5) |
| gen_bathtub_modern_minimal_1_1a44f6ff | bathtub | generated | removed | proportions 1.34 x 0.81 x 0.80 m fit no real bathtub (width (1.4, 1.9), depth (0.65, 0.9), height (0.4, 0.72)) | Generated modern minimal bathtub (1) |
| gen_bathtub_modern_minimal_2_927c5b3c | bathtub | generated | removed | proportions 1.31 x 0.72 x 0.80 m fit no real bathtub (width (1.4, 1.9), depth (0.65, 0.9), height (0.4, 0.72)) | Generated modern minimal bathtub (2) |
| gen_bathtub_modern_minimal_3_5f405b34 | bathtub | generated | removed | proportions 1.35 x 0.85 x 0.80 m fit no real bathtub (width (1.4, 1.9), depth (0.65, 0.9), height (0.4, 0.72)) | Generated modern minimal bathtub (3) |
| gen_bathtub_modern_minimal_5_29a3d1b9 | bathtub | generated | removed | proportions 1.32 x 0.74 x 0.80 m fit no real bathtub (width (1.4, 1.9), depth (0.65, 0.9), height (0.4, 0.72)) | Generated modern minimal bathtub (5) |
| gen_bathtub_scandinavian_1_230fe403 | bathtub | generated | removed | proportions 1.26 x 0.78 x 0.80 m fit no real bathtub (width (1.4, 1.9), depth (0.65, 0.9), height (0.4, 0.72)) | Generated scandinavian bathtub (1) |
| gen_bathtub_scandinavian_2_6fde34a5 | bathtub | generated | removed | proportions 1.39 x 0.80 x 0.80 m fit no real bathtub (width (1.4, 1.9), depth (0.65, 0.9), height (0.4, 0.72)) | Generated scandinavian bathtub (2) |
| gen_bathtub_scandinavian_4_a6fdd251 | bathtub | generated | removed | proportions 1.32 x 0.74 x 0.80 m fit no real bathtub (width (1.4, 1.9), depth (0.65, 0.9), height (0.4, 0.72)) | Generated scandinavian bathtub (4) |
| gen_bathtub_scandinavian_6_c1f08777 | bathtub | generated | removed | proportions 1.28 x 0.78 x 0.80 m fit no real bathtub (width (1.4, 1.9), depth (0.65, 0.9), height (0.4, 0.72)) | Generated scandinavian bathtub (6) |
| gen_bathtub_scandinavian_7_da9e6172 | bathtub | generated | removed | proportions 1.25 x 0.72 x 0.80 m fit no real bathtub (width (1.4, 1.9), depth (0.65, 0.9), height (0.4, 0.72)) | Generated scandinavian bathtub (7) |
| objaverse_84d5cdc68a674e12958f41500e988502 | bathtub | objaverse | removed | licence CC-BY-NC-4.0 not allowed (user decision of 10 Oct 2026) | CARBAWH1-6DT01 |
| abo_B072ZNMKGM | tv_unit | abo | removed | 1676 triangles (< 3000): crude unless the vision quality is high; vision quality 2 | Amazon Brand – Rivet King Street Industrial Cabinet Media Co |
| abo_B07B8FN8TP | tv_unit | abo | removed | the vision check says it is not a tv_unit (a console_table) | Amazon Brand – Stone & Beam Traditional Oak Wood Media TV Co |
| objaverse_4939d1bca386405f9cc22c48441b63de | bookshelf | objaverse | removed | 2008 triangles (< 3000): crude unless the vision quality is high; vision quality 3 | Bookcase |
| objaverse_68baafb344b2445a8e7f4917b6fe8a63 | bookshelf | objaverse | removed | the vision check says it is not a bookshelf (a display_cabinet) | Scaffale B |
| abo_B009S7IZWG | dresser | abo | removed | the vision check says it is not a dresser (a sideboard) | Amazon Brand - Movian Corona Sideboard, 1 Door 4 Drawer, Sol |
| gen_washing_machine_industrial_3_0a739610 | washing_machine | generated | removed | the vision check sees more than one object | Generated industrial washing machine (3) |
| gen_washing_machine_modern_3_50bfae6f | washing_machine | generated | removed | the vision check sees more than one object | Generated modern washing machine (3) |
| gen_washing_machine_modern_minimal_2_94b29e08 | washing_machine | generated | removed | the vision check sees more than one object | Generated modern minimal washing machine (2) |
| gen_washing_machine_scandinavian_5_ed8921b5 | washing_machine | generated | removed | the vision check sees more than one object | Generated scandinavian washing machine (5) |
| abo_B072ZKPK7J | side_table | abo | removed | the vision check sees more than one object | Amazon Brand – Rivet Mid-Century Modern Round Black Wood Nes |
| abo_B07B7J8CGH | side_table | abo | removed | the vision check sees more than one object | Amazon Brand – Rivet Mid-Century Modern Honeycomb Square End |
| abo_B07B7J8FV9 | side_table | abo | removed | the vision check sees more than one object | Amazon Brand – Rivet Modern White Marble and Wood Double Sto |
| abo_B07374SBFN | floor_lamp | abo | removed | vision quality 2 (<= 2) | Amazon Brand – Stone & Beam Glass Column Brass Floor Lamp, W |
| gen_floor_lamp_japandi_1_4be1c62d | floor_lamp | generated | removed | vision quality 2 (<= 2) | Generated japandi floor lamp (1) |
| gen_floor_lamp_japandi_2_ef5fd39d | floor_lamp | generated | removed | vision quality 2 (<= 2) | Generated japandi floor lamp (2) |
| objaverse_01c53767c1f84f55ad9f46eb89949cf9 | floor_lamp | objaverse | removed | the title says street lamp: an outdoor piece | Street Lamp |
| objaverse_0a34dc814a3a44cfa76388e732c05376 | floor_lamp | objaverse | removed | the title says lamppost: an outdoor piece | Lamppost |
| objaverse_53409613b45b42b98b979f12ab8faa12 | floor_lamp | objaverse | removed | the title says low poly: not photoreal | low poly Lamp 3d model |
| objaverse_71853da424aa4b208e14f6cf430339ae | floor_lamp | objaverse | removed | the title says street light: an outdoor piece | Street lights |
| objaverse_41e58efcf647494483f9860df99acf60 | potted_plant | objaverse | removed | the title names empty flower pot, not a potted_plant | Empty Flower Pot |
| objaverse_9dd44cda400c48a083ffd9480067f04f | potted_plant | objaverse | removed | vision quality 2 (<= 2) | Succulent |
| objaverse_b99c584dd11d4691b5d13303383371e5 | potted_plant | objaverse | removed | the vision check says it is not a potted_plant | FlowerPot |
| objaverse_bf122cd0854e422bb94704552c64810b | potted_plant | objaverse | removed | vision quality 2 (<= 2) | CGT 116 Wk8 Plant |
| abo_B084XMYGBF | sofa_corner | abo | removed | the vision check sees more than one object | Amazon Brand - Solimo Alen Five Seater LHS L Shape Sofa Set  |
| gen_chaise_japandi_4_d279126b | chaise | generated | removed | the vision check sees more than one object | Generated japandi chaise (4) |
| objaverse_34fe7fd87a924cf8aeff89ea6f012bae | ottoman | objaverse | removed | 2752 triangles (< 3000): crude unless the vision quality is high; vision quality 3 | Wooden stool |
| objaverse_c4304814dcc441b4a6ebb5cf99081ffe | ottoman | objaverse | removed | licence CC-BY-NC-SA-4.0 not allowed (user decision of 10 Oct 2026) | Decor, footrest |
| objaverse_36dc07c8e85c4b859d78ccd4dd60c63d | bench | objaverse | removed | the title says park bench: an outdoor piece | បង់អង្គុយសាធារណះ - Park Bench |
| objaverse_378cd6e6f505493aa8e22f68db1cabec | bench | objaverse | removed | the title says park bench: an outdoor piece | Simple Park Bench |
| objaverse_7a0c2a659e2441b6b568a9d2acf8419e | bench | objaverse | removed | the title says park bench: an outdoor piece | Park Bench |
| objaverse_83bb7dff14e84ecbbc99ebb80fe2977c | bench | objaverse | removed | licence CC-BY-SA-4.0 not allowed (user decision of 10 Oct 2026) | City Bench 001 |
| objaverse_9a4d1c954ed446d9a8d436d5be6dedca | bench | objaverse | removed | licence CC-BY-NC-SA-4.0 not allowed (user decision of 10 Oct 2026) | Mainstreet USA Bench |
| objaverse_da39bc3a29364f8bb4bf45bccf856bdc | bench | objaverse | removed | the title says gardens: an outdoor piece | Dedicated Bench, Museum Gardens, E2. (Raw Scan) |
| objaverse_f889c3adfc5945dcb10c1a594b35957b | bench | objaverse | removed | licence CC-BY-NC-4.0 not allowed (user decision of 10 Oct 2026) | Street Wooden Bench |
| abo_B072Y5MZQH | office_chair | abo | removed | the vision check says it is not a office_chair (a armchair) | AmazonBasics Classic Leather Office Desk Guest Chair with Me |
| abo_B072Y6Y96S | office_chair | abo | removed | the vision check says it is not a office_chair (a armchair) | AmazonBasics Classic Reception Office Chair with Mahogany Wo |
| gen_crib_classic_4_d4e08139 | crib | generated | removed | the vision check sees more than one object | Generated classic crib (4) |
| gen_crib_mediterranean_4_d3d32233 | crib | generated | removed | the vision check sees more than one object | Generated mediterranean crib (4) |
| objaverse_dbb8dec952c0450ba58fb4f75abf86ec | crib | objaverse | removed | proportions 1.06 x 0.60 x 1.30 m fit no real crib (width (1.15, 1.5), depth (0.6, 0.85), height (0.7, 1.3)) | Cot Final |
| gen_bunk_bed_industrial_4_a364b7d0 | bunk_bed | generated | removed | not a real manufactured product and vision quality 3 (< 4) | Generated industrial bunk bed (4) |
| gen_bunk_bed_minimal_3_209e481a | bunk_bed | generated | removed | vision quality 2 (<= 2) | Generated minimal bunk bed (3) |
| gen_bunk_bed_modern_minimal_3_d55e3538 | bunk_bed | generated | removed | vision quality 2 (<= 2) | Generated modern minimal bunk bed (3) |
| objaverse_1ab0499f7a7746188eefe85c1f16594b | bunk_bed | objaverse | removed | vision quality 2 (<= 2) | A108082006 |
| gen_display_cabinet_mediterranean_4_af84c15b | display_cabinet | generated | removed | the vision check says it is not a display_cabinet (a tall_cabinet) | Generated mediterranean display cabinet (4) |
| abo_B07H8VCDWP | tall_cabinet | abo | removed | the title names aparador, vitrina, not a tall_cabinet | Marca Amazon - Movian Moselle - Aparador con vitrina (roble  |
| abo_B07JGPKSCB | tall_cabinet | abo | removed | the title names a wardrobe, the vision check a tall_cabinet: they disagree | Marque Amazon - Movian - Armoire 3 portes avec miroir Mira,  |
| abo_B07JH147WS | tall_cabinet | abo | removed | the title names a wardrobe, the vision check a tall_cabinet: they disagree | Marchio Amazon - Movian, armadio a 2 ante modello Mira, 98 x |
| abo_B07LC9HXSF | tall_cabinet | abo | removed | the title names dressing table, not a tall_cabinet | Amazon Brand - Solimo Polaris Engineered Wood Dressing Table |
| gen_tall_cabinet_mediterranean_3_38df09c4 | tall_cabinet | generated | removed | vision quality 2 (<= 2) | Generated mediterranean tall cabinet (3) |
| abo_B079V6V6TF | cushion | abo | removed | a copy of abo_B079TXJNJD (box +-1 cm, faces +-1%, same texture) | Amazon Brand – Rivet Modern Geometric Decorative Print Pillo |
| abo_B07BMTNH22 | cushion | abo | removed | a copy of abo_B07BMT4F21 (box +-1 cm, faces +-1%, same texture) | Amazon Brand – Rivet Modern Abstract Geometric Decorative Th |
| abo_B07C8MT64T | cushion | abo | removed | a copy of abo_B07BMTXHSR (box +-1 cm, faces +-1%, same texture) | Amazon Brand – Rivet Modern Mosaic Throw Pillow - 20 x 20 In |
| abo_B073NZTB8J | wall_art | abo | removed | the vision check sees more than one object | Amazon Brand – Stone & Beam Modern Red and Gold Tulip Print  |
| abo_B073P15SD2 | wall_art | abo | removed | the vision check sees more than one object | Amazon Brand – Stone & Beam Modern Gold Print of 1885 Baseba |
| abo_B073P1BKT1 | wall_art | abo | removed | the vision check sees more than one object | Amazon Brand – Stone & Beam Modern Metallic Ink Reprint of S |
| abo_B073P1H7CF | wall_art | abo | removed | the vision check sees more than one object | Black and White Vintage Bike Print in White Frame, 15" x 21" |
| abo_B073P52NDX | wall_art | abo | removed | the vision check sees more than one object | Amazon Brand – Stone & Beam Modern Black and White Desert Ca |
| abo_B073P5MPW9 | wall_art | abo | removed | the vision check sees more than one object | Amazon Brand – Stone & Beam Modern Turquoise and Orange Palm |
| abo_B073P6FYT4 | wall_art | abo | removed | the vision check sees more than one object | Amazon Brand – Rivet Vintage Blue Yellow and Green Chairs in |
| abo_B075X2FW6F | table_lamp | abo | removed | the vision check sees more than one object | Rivet Wood and Black Marble Lamp, Mid-Century Walnut, With B |
| abo_B071HBBDZ1 | mirror | abo | removed | the vision check sees more than one object | Amazon Brand – Stone & Beam Round Wood Quadrant Hanging Wall |
| abo_B071V8LJQJ | mirror | abo | removed | the vision check sees more than one object | Amazon Brand – Stone & Beam Square Wood Quadrant Hanging Wal |
| abo_B071V8M937 | mirror | abo | removed | the vision check sees more than one object | Amazon Brand – Stone & Beam Sunburst Lines Hanging Wall Mirr |
| abo_B07B8NW6GG | mirror | abo | removed | the vision check sees more than one object | Amazon Brand – Stone & Beam Rustic Farmhouse Round Wood Iron |
| abo_B07RNMMYPR | mirror | abo | removed | vision quality 2 (<= 2) | Amazon Basics Rectangular Wall Mirror 30" x 40" - Peaked Tri |
| abo_B084HTZ2C6 | mirror | abo | removed | the vision check sees more than one object | Amazon Brand - Rivet Modern Round Hanging Mirror with Shelf, |
| abo_B084HV148L | mirror | abo | removed | the vision check sees more than one object | Amazon Brand - Rivet Modern Round Cutout Hanging Mirror, 22. |
| abo_B084HV67GW | mirror | abo | removed | the vision check sees more than one object | Amazon Brand - Rivet Modern Cutout Hanging Mirror, 23"H, Gol |
| gen_curtain_mediterranean_1_55dc3d88 | curtain | generated | removed | vision quality 2 (<= 2) | Generated mediterranean curtain (1) |
| gen_curtain_rustic_2_f1cb2022 | curtain | generated | removed | not a real manufactured product and vision quality 3 (< 4) | Generated rustic curtain (2) |
| objaverse_5b9e03a46de84bd58d3894cab9f40a78 | curtain | objaverse | removed | the title names window, not a curtain | Window |
| objaverse_b0bd00b700a3451da1cb4ad9b082c3e0 | curtain | objaverse | removed | the vision check sees more than one object | Quentin Sees Neighbor |
| objaverse_dac09c92cc82445994d76c1083ca8888 | curtain | objaverse | removed | the title names window, not a curtain | Window |
| objaverse_e826c513779149d7ab3bde944647573f | curtain | objaverse | removed | the title names window, not a curtain | Window |
| gen_blind_minimal_4_343b5f93 | blind | generated | removed | vision quality 2 (<= 2) | Generated minimal blind (4) |
| gen_blind_modern_4_e018681c | blind | generated | removed | vision quality 2 (<= 2) | Generated modern blind (4) |
| gen_blind_modern_minimal_4_ff409718 | blind | generated | removed | vision quality 2 (<= 2) | Generated modern minimal blind (4) |
| gen_blind_scandinavian_1_f05a9bbd | blind | generated | removed | proportions 0.42 x 0.40 x 0.43 m fit no real blind (width (0.3, 3.0), depth (0.01, 0.35), height (0.4, 3.0)) | Generated scandinavian blind (1) |
| gen_throw_minimal_3_9eeda630 | throw | generated | removed | the vision check says it is not a throw | Generated minimal throw (3) |
| gen_throw_modern_minimal_1_69ba5696 | throw | generated | removed | the vision check says it is not a throw | Generated modern minimal throw (1) |
| gen_throw_modern_minimal_3_9e78dc45 | throw | generated | removed | vision quality 2 (<= 2) | Generated modern minimal throw (3) |
| objaverse_0039218299e647d788844de8e1ef7cc2 | throw | objaverse | removed | the title says linnamagi: not the object | Ehavere linnamägi (Estonia) |
| objaverse_0d5590d1d2184aa98797c3d6382afd7e | throw | objaverse | removed | the title names futon, bed, not a throw | Japanese futon/bed |
| objaverse_2fbb8f56b1ba47bdb6746d95b6fc2242 | throw | objaverse | removed | the title names towel, not a throw | Hanging Towel |
| objaverse_68ba20aeb8fe4a03befaa2db5b429758 | throw | objaverse | removed | the title names kitty, not a throw | Comfy kitty |
| objaverse_6b46b33bdff44269bf9391774bb8dd63 | throw | objaverse | removed | the title names machine, not a throw | JuiceMachine |
| objaverse_be9b034525c246cebab3620acb5a8027 | throw | objaverse | removed | the title says corpse: not the object | Corpse |
| objaverse_eee70cb7980a4ca7aa0a2f86c492283e | throw | objaverse | removed | the title names bench, not a throw | Bench with Cloth |
| objaverse_fcff1bddc64c4c9e98f85ff848a8a0eb | throw | objaverse | removed | the title names bench, not a throw | Saoura Traditional bench |
| gen_books_scandinavian_2_a69db21c | books | generated | removed | the vision check says it is not a books | Generated scandinavian books (2) |
| objaverse_1c77a05af556408dbfa04ad1999a8a32 | books | objaverse | removed | licence CC-BY-SA-4.0 not allowed (user decision of 10 Oct 2026) | Books |
| objaverse_36ef9c80cceb48909e11b358aee00223 | books | objaverse | removed | licence CC-BY-NC-SA-4.0 not allowed (user decision of 10 Oct 2026) | Book |
| objaverse_6931e14a96f64b158ac4cebcf7ae8763 | books | objaverse | removed | licence CC-BY-SA-4.0 not allowed (user decision of 10 Oct 2026) | Opened comics book |
| objaverse_775a10863f4b4819a409788ad183e2d5 | books | objaverse | removed | licence CC-BY-NC-SA-4.0 not allowed (user decision of 10 Oct 2026) | Box on Ready Player Two |
| objaverse_c1e84a838f644940ae5b40e19bcdfff8 | books | objaverse | removed | the vision check says it is not a books | Filmbook_St01 |
| objaverse_dfcd6f9d7aba46938912a0f68d0ce676 | books | objaverse | removed | licence CC-BY-NC-SA-4.0 not allowed (user decision of 10 Oct 2026) | The Woodbook #3DST29 |
| objaverse_f8052beda9344eba88c5692c6a29a2cf | books | objaverse | removed | the title names box, not a books | Exclusive Kickstarter DELUXE Box |
| objaverse_b1eb4cef55f94a11b767dc111a86e669 | candle | objaverse | removed | vision quality 2 (<= 2) | CandleHolder_skyrim |
| objaverse_bbfe3dd1980b4c7c891a5ec93aa7763a | candle | objaverse | removed | vision quality 2 (<= 2) | Gothic Lantern (Mnemolli concept) |
| objaverse_c532273884b0455b8e65664bbb91f4c4 | candle | objaverse | removed | licence CC-BY-NC-4.0 not allowed (user decision of 10 Oct 2026) | Medieval candle |
| objaverse_c5b1ca5b8492426199932f6b1a64a4d9 | candle | objaverse | removed | the title says lowpoly: not photoreal | Lowpoly Candle |
| objaverse_d9d5ed5de83b4d899ab93f55bdc3d0bc | candle | objaverse | removed | vision quality 2 (<= 2) | Candle light |
| objaverse_01c77468a1d04414ae24ecd1d1559f7d | basket | objaverse | removed | the title says stylized: not photoreal | Stylized Sand Bricks Material |
| objaverse_0cd51caee3e14b2d92efaef53c7c0196 | basket | objaverse | removed | the title names a tray, the vision check a basket: they disagree | Rattan Tray |
| objaverse_7f39b77440c4416cab9dbba79f3262a2 | basket | objaverse | removed | the title names bowl, not a basket | Terracotta Bowl |
| objaverse_cabd5910411b497a9698931246faa95a | basket | objaverse | removed | a drawer, door or lid is open, or a part floats apart | Dobi Basket |
| objaverse_085dca6d7eaa49a2bc459adfe3357da9 | tray | objaverse | removed | the title names shelf, not a tray | SIMPLE Shelf |
| objaverse_3a406e651e69409e87323ab42a214874 | tray | objaverse | removed | the vision check says it is not a tray | Pia Texturizada por Wellington Marques |
| objaverse_3dc49a977873417088384f5ae78c5a6c | tray | objaverse | removed | the title names bento, not a tray | Unagyu-bento |
| objaverse_3e7747b1db4b44a4952d6d94488ee16e | tray | objaverse | removed | vision quality 2 (<= 2) | Dinner Tray |
| objaverse_3ed0c8a70da84ee99816fa29e352ac16 | tray | objaverse | removed | the title names couch, not a tray | Low Poly Couch |
| objaverse_545d37a90a7d4c00b5e5bc551c71fbbf | tray | objaverse | removed | the title names светильник, not a tray | Светильник DL303-L7W Maytoni |
| objaverse_8c63e5e160064cd3862e4b5f8781032b | tray | objaverse | removed | the title names светильник, not a tray | Светильник DL303-L12W Maytoni /40 |
| objaverse_985b48efbd774f8f9fa74304508cad34 | tray | objaverse | removed | the title names sink, not a tray | FRUTTI GIALLI - SQUARE SINK FROM ITALY |
| objaverse_acca44bccd9e4d82ba0e2ed0eb1e478c | tray | objaverse | removed | the vision check says it is not a tray | pote.c4d |
| objaverse_c1e6ac573c37485f9e7acaaae418df30 | tray | objaverse | removed | the title names cutting board, not a tray | Cutting board |
| objaverse_c274989766c344ac97817f77a046c0e0 | tray | objaverse | removed | vision quality 2 (<= 2) | Platform |
| objaverse_e736a1e7cdcb48a5a4f2ca4100d52d28 | tray | objaverse | removed | the vision check says it is not a tray | Доработка дно пирожницы h=23 l=75 без рёбер |
| abo_B076V9MWFL | clock | abo | removed | the vision check sees more than one object | Amazon Brand - Solimo 12" Wall Clock - Paramount Dark Paneli |
| abo_B07B8NSY3Z | clock | abo | removed | the vision check sees it lying on its side or upside down | Amazon Brand – Stone & Beam Large Battery Operated Square Ar |
| abo_B07B8NZMZF | clock | abo | removed | the vision check sees it lying on its side or upside down | Amazon Brand – Stone & Beam Vintage Farmhouse Style Decorati |
| abo_B07B8P1SB7 | clock | abo | removed | the vision check sees more than one object | Amazon Brand – Rivet Modern Minamalist Wood-Face Clock, 12"H |
| abo_B07B8PXJJW | clock | abo | removed | the vision check sees more than one object | Rivet Modern Brass Clock, 12"H, Green |
| abo_B07B8PXTVL | clock | abo | removed | the vision check sees it lying on its side or upside down | Amazon Brand – Stone & Beam Round Battery Operated Vintage D |
| objaverse_01fb2f80dad74a2280a4c077d871b262 | clock | objaverse | removed | the title names grandfather clock, not a clock | Grandfather Clock |
| objaverse_2533ef500ece4fcc804872c706df036b | clock | objaverse | removed | the vision check sees it lying on its side or upside down | (FREE) Wall Clock / ساعة جدارية |
| objaverse_5c1723090dd3487aabcb2b2d5bc35c07 | clock | objaverse | removed | the vision check sees it lying on its side or upside down | Bedside Wooden Clock |
| objaverse_8c95c5e879f24f8294d9c8c25804ab95 | clock | objaverse | removed | the vision check sees more than one object | CC0 - Wall Clock 3 |
| objaverse_c440d78639b74e77ba6ae375f9cbf5b7 | clock | objaverse | removed | not a real manufactured product and vision quality 3 (< 4) | Broken Steampunk Clock |
| objaverse_dfe6f89d65be4a23b28abf07178efebf | clock | objaverse | removed | the title says galvanometer: not the object | Western Electric Tangent Galvanometer |
| gen_sculpture_japandi_1_136a4ec5 | sculpture | generated | removed | not a real manufactured product and vision quality 3 (< 4) | Generated japandi sculpture (1) |
| gen_sculpture_scandinavian_1_6ac6cfa2 | sculpture | generated | removed | the vision check sees more than one object | Generated scandinavian sculpture (1) |
| objaverse_36bb9a6e62ab4b88b7154c41489b5f41 | sculpture | objaverse | removed | the title says low poly: not photoreal | Fountain - low-poly |
| objaverse_65fe1034b180420bbf2eb00e87092ad5 | sculpture | objaverse | removed | the vision check says it is an outdoor piece | Sea lion statue, Marina, San Francisco (1) |
| objaverse_bac9ee64eb454a66a637ae0c20f56364 | sculpture | objaverse | removed | the title says cemiterio: an outdoor piece | Anjo de Cemitério/ Angel Cemitery |
| gen_plant_large_industrial_4_8cd58cf0 | plant_large | generated | removed | not a real manufactured product and vision quality 3 (< 4) | Generated industrial plant large (4) |
| abo_B0716WLY2Y | pendant_light | abo | removed | the vision check sees more than one object | Amazon Brand – Stone & Beam Industrial Farmhouse Double Pend |
| abo_B0719K9G5L | pendant_light | abo | removed | vision quality 2 (<= 2) | Amazon Brand – Stone & Beam Vintage Ceiling Pendant Lighting |
| abo_B071LDM8NL | pendant_light | abo | removed | vision quality 2 (<= 2) | Amazon Brand – Stone & Beam Jordan Industrial Farmhouse Ceil |
| objaverse_069fe37a0f144d8387db9b4594c501af | pendant_light | objaverse | removed | the title names wall sconce, not a pendant_light | Copper wall sconce |
| objaverse_600a996f3b9e44fd912beb8129b5f929 | pendant_light | objaverse | removed | licence CC-BY-NC-4.0 not allowed (user decision of 10 Oct 2026) | Small Chandelier |
| abo_B07QGHTCY4 | ceiling_light | abo | removed | the vision check sees more than one object | Amazon Brand – Ravenna Home Casual Flush Mount, 3"H, Oil-Rub |
| abo_B0828DHVWJ | ceiling_light | abo | removed | the vision check says it is not a ceiling_light | Amazon Brand - Ravenna Home Single-Light Flush-Mount Ceiling |
| abo_B0828F59QW | ceiling_light | abo | removed | the vision check says it is not a ceiling_light (a pendant_light) | Amazon Brand - Ravenna Home 2-Light Semiflush-Mount Ceiling  |
| abo_B0828F62FS | ceiling_light | abo | removed | the vision check sees more than one object | Amazon Brand - Ravenna Home Single-Light Flush-Mount Ceiling |
| gen_ceiling_light_japandi_1_200ebd4d | ceiling_light | generated | removed | the vision check says it is not a ceiling_light (a pendant_light) | Generated japandi ceiling light (1) |
| gen_ceiling_light_scandinavian_1_3482d35d | ceiling_light | generated | removed | the vision check says it is not a ceiling_light (a pendant_light) | Generated scandinavian ceiling light (1) |
| gallinera_chair | chair | polyhaven | removed | the vision check says it is not a chair (a armchair) | Gallinera Chair |
| dining_table | table_dining | polyhaven | removed | 1048 triangles (< 3000): crude unless the vision quality is high; vision quality 2 | Dining Table |
| WoodenTable_01 | desk | polyhaven | removed | proportions 1.80 x 0.66 x 0.55 m fit no real desk (width (0.9, 2.0), depth (0.5, 0.9), height (0.65, 1.2)) | Wooden Table 01 |
| throw_pillows_01 | cushion | polyhaven | removed | the vision check sees more than one object | Throw Pillows 01 |

## Models to fix

| id | type | source | fixes | why |
|---|---|---|---|---|
| abo_B0718WYQ8D | bed_single | abo | {"front_quarter_turns": 1} | 2 part(s) stick out of the main body (+z, -z, up to 0.36 m): an open drawer or a separate prop?; the vision check sees t |
| abo_B07H8V7MQS | bed_single | abo | {"front_quarter_turns": 3} | the vision check sees the front on the left of view 0: front turned |
| gen_bed_single_industrial_1_9f087076 | bed_single | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units unknown: scaled to a typical footprint of the type (normalised) |
| gen_bed_single_rustic_1_db9b30c6 | bed_single | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units unknown: scaled to a typical footprint of the type (normalised) |
| gen_bed_single_rustic_3_20248be5 | bed_single | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units unknown: scaled to a typical footprint of the type (normalised) |
| objaverse_b547d81073b64d3e97200fd3ae9a74af | bed_single | objaverse | {"front_quarter_turns": 1} | units guessed (x0.01); 10 part(s) stick out of the main body (+z, -z, up to 0.34 m): an open drawer or a separate prop? |
| objaverse_08f7f65edfea417b8ed9ca748381e507 | bed_double | objaverse | {"rescale": 0.8483} | the unit guess put it 18% off a real bed_double: rescaled x0.848; units guessed (x0.001) |
| objaverse_5d3a99865ac84d8a8bf06b263aa5bb55 | bed_double | objaverse | {"front_quarter_turns": 1} | units guessed (x0.01); the vision check sees the front on the right of view 0: front turned |
| abo_B01MXKMRK4 | desk | abo | {"front_quarter_turns": 1} | 10 part(s) stick out of the main body (-z, up to 0.71 m): an open drawer or a separate prop?; the vision check sees the  |
| abo_B07GFL6RF5 | desk | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B07GFS1V51 | desk | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B07K7K7GKC | chair | abo | {"front_quarter_turns": 3} | 6 part(s) stick out of the main body (+z, -z, up to 0.47 m): an open drawer or a separate prop?; the vision check sees t |
| abo_B084RZVHD2 | chair | abo | {"front_quarter_turns": 3} | 10 part(s) stick out of the main body (+y, +z, -z, up to 0.45 m): an open drawer or a separate prop?; the vision check s |
| abo_B084W2GNQW | chair | abo | {"front_quarter_turns": 3} | 1 part(s) stick out of the main body (+z, up to 0.06 m): an open drawer or a separate prop?; the vision check sees the f |
| abo_B0857JLP6K | chair | abo | {"front_quarter_turns": 3} | 10 part(s) stick out of the main body (+y, +z, -z, up to 0.57 m): an open drawer or a separate prop?; the vision check s |
| objaverse_1625701880c54b7d9f50e77455cef39b | chair | objaverse | {"front_quarter_turns": 1} | units guessed (x1.0); the vision check sees the front on the right of view 0: front turned |
| objaverse_47a690dcecf847fca99c4f89111db85b | chair | objaverse | {"front_quarter_turns": 3} | units unknown: scaled to a typical footprint of the type (normalised); the vision check sees the front on the left of vi |
| objaverse_acf6497a3d274d90ad3750510348f07a | chair | objaverse | {"front_quarter_turns": 3} | units guessed (x1.0); the vision check sees the front on the left of view 0: front turned |
| objaverse_d2785b57e7da45858f2fe8bf4dedd68d | chair | objaverse | {"front_quarter_turns": 3} | units guessed (x0.01); 10 part(s) stick out of the main body (+z, -z, up to 0.41 m): an open drawer or a separate prop? |
| abo_B07GFS1R5B | wardrobe | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B07GFS1WDY | wardrobe | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B07GFWW3S8 | wardrobe | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B07H8JN9QF | wardrobe | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B07H8PS4FZ | wardrobe | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B07H8V7P3H | wardrobe | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| gen_wardrobe_classic_1_2bc1a548 | wardrobe | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units unknown: scaled to a typical footprint of the type (normalised) |
| gen_wardrobe_rustic_1_97c119f6 | wardrobe | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units unknown: scaled to a typical footprint of the type (normalised) |
| gen_wardrobe_scandinavian_1_d0aa2dad | wardrobe | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units unknown: scaled to a typical footprint of the type (normalised) |
| gen_fridge_classic_3_25281fe9 | fridge | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units unknown: scaled to a typical footprint of the type (normalised) |
| gen_fridge_industrial_1_03996e16 | fridge | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units unknown: scaled to a typical footprint of the type (normalised) |
| gen_fridge_japandi_6_60928003 | fridge | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units unknown: scaled to a typical footprint of the type (normalised) |
| gen_fridge_mediterranean_1_1460e264 | fridge | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units unknown: scaled to a typical footprint of the type (normalised) |
| gen_fridge_mediterranean_3_e70ec886 | fridge | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units guessed (x1.0) |
| objaverse_66878d980a364b2db1a5cc44c67bb45d | fridge | objaverse | {"front_quarter_turns": 1} | units guessed (x0.0254); untextured (material colours only) |
| objaverse_7c5c9dec5c2e4ff998c386410b0e3686 | stove | objaverse | {"front_quarter_turns": 1} | units unknown: scaled to a typical footprint of the type (normalised); the vision check sees the front on the right of v |
| gen_toilet_classic_3_293965c2 | toilet | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units unknown: scaled to a typical footprint of the type (normalised) |
| gen_toilet_japandi_3_4e49add0 | toilet | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units unknown: scaled to a typical footprint of the type (normalised) |
| gen_toilet_japandi_6_1b5173e9 | toilet | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units unknown: scaled to a typical footprint of the type (normalised) |
| gen_toilet_mediterranean_1_09b9f7e2 | toilet | generated | {"front_quarter_turns": 2} | generated (TRELLIS.2): no real product; its front is on the wrong side for a toilet (width along the front): turned 90 d |
| gen_toilet_mediterranean_3_23b530a6 | toilet | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units guessed (x1.0) |
| gen_toilet_scandinavian_4_06dcb780 | toilet | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units guessed (x1.0) |
| gen_toilet_scandinavian_6_b1b3db93 | toilet | generated | {"front_quarter_turns": 2} | generated (TRELLIS.2): no real product; its front is on the wrong side for a toilet (width along the front): turned 90 d |
| abo_B074KKXLK1 | bookshelf | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B07H8SQ2NZ | bookshelf | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B07JGY5LNV | bookshelf | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B082JGV1YM | bookshelf | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| objaverse_7a545709aa98429a9b30f812f70193f7 | bookshelf | objaverse | {"front_quarter_turns": 1} | units unknown: scaled to a typical footprint of the type (normalised); the vision check sees the front on the right of v |
| objaverse_b43c45317fd74a4aa9ba443b9a355ea3 | bookshelf | objaverse | {"front_quarter_turns": 1} | units unknown: scaled to a typical footprint of the type (normalised); the vision check sees the front on the right of v |
| abo_B072ZMHBKQ | nightstand | abo | {"front_quarter_turns": 1} | 4 part(s) stick out of the main body (-z, up to 0.30 m): an open drawer or a separate prop?; the vision check sees the f |
| abo_B074KKMQBG | nightstand | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B075X38PZ7 | nightstand | abo | {"front_quarter_turns": 1} | 10 part(s) stick out of the main body (-z, up to 0.57 m): an open drawer or a separate prop?; the vision check sees the  |
| abo_B079VK52WZ | nightstand | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B079VKDKC1 | nightstand | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B079VNKB6Z | nightstand | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B079VNL3CG | nightstand | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B07K7K7GTZ | nightstand | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B07L1DH1PX | nightstand | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B07QD6TXWS | nightstand | abo | {"front_quarter_turns": 1} | 10 part(s) stick out of the main body (+z, -z, up to 0.35 m): an open drawer or a separate prop?; the vision check sees  |
| abo_B07QS8TBXT | nightstand | abo | {"front_quarter_turns": 1} | 7 part(s) stick out of the main body (+z, -z, up to 0.27 m): an open drawer or a separate prop?; the vision check sees t |
| abo_B07RNZC4TJ | nightstand | abo | {"front_quarter_turns": 1} | 10 part(s) stick out of the main body (-z, up to 0.24 m): an open drawer or a separate prop?; the vision check sees the  |
| abo_B07RPZSM4W | nightstand | abo | {"front_quarter_turns": 1} | 10 part(s) stick out of the main body (+z, -z, up to 0.26 m): an open drawer or a separate prop?; the vision check sees  |
| abo_B07VB7Q6W7 | nightstand | abo | {"front_quarter_turns": 1} | 4 part(s) stick out of the main body (-z, up to 0.19 m): an open drawer or a separate prop?; the vision check sees the f |
| abo_B084MYDTKM | nightstand | abo | {"front_quarter_turns": 1} | 4 part(s) stick out of the main body (-z, up to 0.17 m): an open drawer or a separate prop?; the vision check sees the f |
| abo_B00838756S | dresser | abo | {"front_quarter_turns": 1} | 10 part(s) stick out of the main body (+z, up to 0.66 m): an open drawer or a separate prop?; the vision check sees the  |
| abo_B01557QQSW | dresser | abo | {"front_quarter_turns": 1} | the title names a near type (credenze); the vision check sees the front on the right of view 0: front turned |
| abo_B01MG6BPC6 | dresser | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B071FJR3S6 | dresser | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B071FJR3SR | dresser | abo | {"front_quarter_turns": 1} | 10 part(s) stick out of the main body (+y, -z, up to 0.43 m): an open drawer or a separate prop?; the vision check sees  |
| abo_B071FJR479 | dresser | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B071P9WJBT | dresser | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B071SHBTM5 | dresser | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B075YZYJQN | dresser | abo | {"front_quarter_turns": 1} | 10 part(s) stick out of the main body (+x, up to 0.73 m): an open drawer or a separate prop?; the vision check sees the  |
| abo_B079X4CP3F | dresser | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B07B4VXZZC | dresser | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B07FFWSBBF | dresser | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B07FK1HLZ4 | dresser | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B07HSDP2CP | dresser | abo | {"front_quarter_turns": 1} | the M8-M10 judges named different fronts {'qwen': 2, 'glm': 0}; the vision check sees the front on the right of view 0:  |
| abo_B07HSH4WFB | dresser | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B07PYKPBY9 | dresser | abo | {"front_quarter_turns": 1} | 6 part(s) stick out of the main body (+y, -z, up to 0.34 m): an open drawer or a separate prop?; the vision check sees t |
| gen_washing_machine_classic_1_dffff7e0 | washing_machine | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units unknown: scaled to a typical footprint of the type (normalised) |
| gen_washing_machine_industrial_1_b7c9d275 | washing_machine | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units unknown: scaled to a typical footprint of the type (normalised) |
| gen_washing_machine_japandi_1_f1f4def2 | washing_machine | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units unknown: scaled to a typical footprint of the type (normalised) |
| gen_washing_machine_japandi_2_d8b8ac48 | washing_machine | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units unknown: scaled to a typical footprint of the type (normalised) |
| gen_washing_machine_japandi_3_3e2ddcc7 | washing_machine | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units unknown: scaled to a typical footprint of the type (normalised) |
| gen_washing_machine_japandi_5_030a02dc | washing_machine | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units unknown: scaled to a typical footprint of the type (normalised) |
| gen_washing_machine_mediterranean_1_bffe5bde | washing_machine | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units unknown: scaled to a typical footprint of the type (normalised) |
| gen_washing_machine_minimal_1_9ec6e746 | washing_machine | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units unknown: scaled to a typical footprint of the type (normalised) |
| gen_washing_machine_modern_1_f4bdd46e | washing_machine | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units unknown: scaled to a typical footprint of the type (normalised) |
| gen_washing_machine_modern_2_379d2585 | washing_machine | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units unknown: scaled to a typical footprint of the type (normalised) |
| gen_washing_machine_modern_minimal_1_07b2b182 | washing_machine | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units unknown: scaled to a typical footprint of the type (normalised) |
| gen_washing_machine_modern_minimal_3_ff74255c | washing_machine | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units unknown: scaled to a typical footprint of the type (normalised) |
| gen_washing_machine_scandinavian_1_0a5054b6 | washing_machine | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units unknown: scaled to a typical footprint of the type (normalised) |
| gen_washing_machine_scandinavian_2_67f28c86 | washing_machine | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units unknown: scaled to a typical footprint of the type (normalised) |
| gen_washing_machine_scandinavian_3_292e2d11 | washing_machine | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units unknown: scaled to a typical footprint of the type (normalised) |
| gen_washing_machine_scandinavian_4_d66cae6a | washing_machine | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units unknown: scaled to a typical footprint of the type (normalised) |
| abo_B07B4FZXK2 | sofa_corner | abo | {"front_quarter_turns": 1} | its front is on the wrong side for a sofa_corner (width along the front): turned 90 deg (to the geometric front +X); the |
| abo_B07BW8MJQT | sofa_corner | abo | {"front_quarter_turns": 3} | its front is on the wrong side for a sofa_corner (width along the front): turned 270 deg (to the geometric front -X); th |
| abo_B07M7MMPWY | chaise | abo | {"front_quarter_turns": 3} | the M8-M10 judges named different fronts {'qwen': 0, 'glm': 3}; 7 part(s) stick out of the main body (+y, +z, -z, up to  |
| abo_B07MFXP3X9 | chaise | abo | {"front_quarter_turns": 3} | the M8-M10 judges named different fronts {'qwen': 3, 'glm': 1}; 7 part(s) stick out of the main body (+y, +z, -z, up to  |
| gen_chaise_industrial_4_77836ff4 | chaise | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units unknown: scaled to a typical footprint of the type (normalised) |
| gen_chaise_japandi_1_542da328 | chaise | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units unknown: scaled to a typical footprint of the type (normalised) |
| gen_chaise_scandinavian_4_c69c1983 | chaise | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units unknown: scaled to a typical footprint of the type (normalised) |
| abo_B075YP38WS | bar_stool | abo | {"front_quarter_turns": 3} | 10 part(s) stick out of the main body (+y, +z, -z, up to 0.57 m): an open drawer or a separate prop?; the vision check s |
| abo_B07DM6YVJH | bar_stool | abo | {"front_quarter_turns": 1} | 6 part(s) stick out of the main body (-z, up to 0.72 m): an open drawer or a separate prop?; the vision check sees the f |
| abo_B00IFHPVEU | office_chair | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B00XBC3BF0 | office_chair | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B016ID2V5O | office_chair | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B01D7P5BFS | office_chair | abo | {"front_quarter_turns": 3} | the M8-M10 judges named different fronts {'qwen': 2, 'glm': 0}; 10 part(s) stick out of the main body (+x, +y, +z, -x, - |
| abo_B01DN7NFRG | office_chair | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B06W5XBL3D | office_chair | abo | {"front_quarter_turns": 1} | 10 part(s) stick out of the main body (+x, +y, +z, -x, -z, up to 0.47 m): an open drawer or a separate prop?; the vision |
| abo_B072Z6K94S | office_chair | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B07GPSQKV9 | office_chair | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B07KWZH5PV | office_chair | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B07KXF19FN | office_chair | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B081HMS8YK | office_chair | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B082KYYMZ6 | office_chair | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B084T7GSXM | office_chair | abo | {"front_quarter_turns": 3} | the vision check sees the front on the left of view 0: front turned |
| gen_crib_modern_minimal_1_ddd7d0c3 | crib | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units guessed (x1.0) |
| gen_crib_modern_minimal_4_13c42be0 | crib | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units guessed (x1.0) |
| gen_bunk_bed_mediterranean_1_d9f8e70f | bunk_bed | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; its front is on the wrong side for a bunk_bed (width along the front): turned 90 |
| gen_bunk_bed_mediterranean_4_b3b0eca5 | bunk_bed | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; its front is on the wrong side for a bunk_bed (width along the front): turned 90 |
| gen_bunk_bed_rustic_4_c03d21d4 | bunk_bed | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; its front is on the wrong side for a bunk_bed (width along the front): turned 90 |
| objaverse_7ea465a1489c4b12bb5a8ff33325cccb | bunk_bed | objaverse | {"front_quarter_turns": 1} | its front is on the wrong side for a bunk_bed (width along the front): turned 90 deg (side unknown: the vision check con |
| objaverse_c505ffffc1524865ba63af837346f1f7 | bunk_bed | objaverse | {"front_quarter_turns": 1} | the title names a near type (double bed); its front is on the wrong side for a bunk_bed (width along the front): turned  |
| objaverse_ea40259ea9ab488e8fe21eaf2fc29d6e | bunk_bed | objaverse | {"front_quarter_turns": 1} | its front is on the wrong side for a bunk_bed (width along the front): turned 90 deg (side unknown: the vision check con |
| abo_B075Z8628K | sideboard | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B07B78RCT5 | sideboard | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B07B7B94L2 | sideboard | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B07HSF15FW | sideboard | abo | {"front_quarter_turns": 1} | 1 part(s) stick out of the main body (-z, up to 0.18 m): an open drawer or a separate prop?; the vision check sees the f |
| abo_B07JFGPVZD | sideboard | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B07RMJSGS7 | sideboard | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B07GFF11HV | shoe_cabinet | abo | {"front_quarter_turns": 1} | 6 part(s) stick out of the main body (+y, -z, up to 0.20 m): an open drawer or a separate prop?; the vision check sees t |
| abo_B07GFLG5MM | shoe_cabinet | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B07GFS1R7X | shoe_cabinet | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B07GFS1WH7 | shoe_cabinet | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B07P652THV | shoe_cabinet | abo | {"front_quarter_turns": 1} | 10 part(s) stick out of the main body (-z, up to 0.45 m): an open drawer or a separate prop?; the vision check sees the  |
| abo_B07TVN114C | shoe_cabinet | abo | {"front_quarter_turns": 1} | 10 part(s) stick out of the main body (+x, +y, +z, -z, up to 0.56 m): an open drawer or a separate prop?; the vision che |
| gen_shoe_cabinet_industrial_1_23a27737 | shoe_cabinet | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units guessed (x1.0) |
| gen_shoe_cabinet_industrial_3_596e817a | shoe_cabinet | generated | {"rescale": 0.8162} | generated (TRELLIS.2): no real product; the unit guess put it 23% off a real shoe_cabinet: rescaled x0.816 |
| gen_shoe_cabinet_japandi_2_d4caf94a | shoe_cabinet | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units guessed (x1.0) |
| gen_shoe_cabinet_mediterranean_1_5b538be0 | shoe_cabinet | generated | {"front_quarter_turns": 1, "rescale": 0.7739} | generated (TRELLIS.2): no real product; the unit guess put it 29% off a real shoe_cabinet: rescaled x0.774 |
| gen_shoe_cabinet_mediterranean_3_4228c675 | shoe_cabinet | generated | {"front_quarter_turns": 1, "rescale": 0.8228} | generated (TRELLIS.2): no real product; the unit guess put it 22% off a real shoe_cabinet: rescaled x0.823 |
| gen_shoe_cabinet_scandinavian_2_66dac02b | shoe_cabinet | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units guessed (x1.0) |
| abo_B07JG3ZVVZ | display_cabinet | abo | {"front_quarter_turns": 1} | 1 part(s) stick out of the main body (-z, up to 0.07 m): an open drawer or a separate prop?; the vision check sees the f |
| gen_display_cabinet_industrial_4_be8f656e | display_cabinet | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units unknown: scaled to a typical footprint of the type (normalised) |
| gen_display_cabinet_japandi_1_211fbef4 | display_cabinet | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units unknown: scaled to a typical footprint of the type (normalised) |
| gen_display_cabinet_scandinavian_1_e7525a8d | display_cabinet | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units unknown: scaled to a typical footprint of the type (normalised) |
| gen_display_cabinet_scandinavian_5_4b2b7b6d | display_cabinet | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units unknown: scaled to a typical footprint of the type (normalised) |
| abo_B07GFFY4WT | tall_cabinet | abo | {"front_quarter_turns": 3} | the title names a near type (~skoskap); the vision check sees the front on the left of view 0: front turned |
| abo_B07GFW9GFX | tall_cabinet | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B07H8PQC9V | tall_cabinet | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| abo_B07H8PQFR2 | tall_cabinet | abo | {"front_quarter_turns": 1} | the title names a near type (vitrina); the M8-M10 judges named different fronts {'qwen': 0, 'glm': 2} |
| abo_B07RMJPJMX | tall_cabinet | abo | {"front_quarter_turns": 1} | the vision check sees the front on the right of view 0: front turned |
| gen_tall_cabinet_classic_3_879ecbf5 | tall_cabinet | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units unknown: scaled to a typical footprint of the type (normalised) |
| gen_tall_cabinet_industrial_1_9054f861 | tall_cabinet | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units unknown: scaled to a typical footprint of the type (normalised) |
| gen_tall_cabinet_industrial_3_8656669b | tall_cabinet | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units unknown: scaled to a typical footprint of the type (normalised) |
| gen_tall_cabinet_japandi_1_a52b169e | tall_cabinet | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units unknown: scaled to a typical footprint of the type (normalised) |
| gen_tall_cabinet_rustic_3_60387ddf | tall_cabinet | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units unknown: scaled to a typical footprint of the type (normalised) |
| gen_tall_cabinet_scandinavian_3_0feb441e | tall_cabinet | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; units unknown: scaled to a typical footprint of the type (normalised) |
| objaverse_74c95870e2a141a9903815715d25b8a7 | tray | objaverse | {"type": "basket"} | units unknown: scaled to a typical footprint of the type (normalised); retyped tray -> basket: the title and the vision  |
| painted_wooden_chair_02 | chair | polyhaven | {"front_quarter_turns": 1} | 10 part(s) stick out of the main body (+y, +z, -z, up to 0.68 m): an open drawer or a separate prop?; the vision check s |
| SchoolDesk_01 | desk | polyhaven | {"rescale": 1.2276} | it is 23% off a real desk: rescaled x1.228; 6 part(s) stick out of the main body (-z, up to 0.69 m): an open drawer or a |
| wooden_display_shelves_01 | bookshelf | polyhaven | {"front_quarter_turns": 1} | 10 part(s) stick out of the main body (-x, up to 1.05 m): an open drawer or a separate prop?; the vision check sees the  |
| Shelf_01 | bookshelf | polyhaven | {"front_quarter_turns": 1} | 34% open edges; the vision check sees the front on the right of view 0: front turned |
| wooden_bookshelf_worn | bookshelf | polyhaven | {"front_quarter_turns": 1, "rescale": 0.7974} | it is 25% off a real bookshelf: rescaled x0.797; 10 part(s) stick out of the main body (+x, -z, up to 1.29 m): an open d |
| WoodenTable_03 | tv_unit | polyhaven | {"front_quarter_turns": 1} | the title names a near type (table); the vision check sees the front on the right of view 0: front turned |
