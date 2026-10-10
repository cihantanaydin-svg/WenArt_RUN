# Library audit (dry, CPU)

CPU dry audit (no render, no vision check): the checks code can make on the catalogue fields alone (licence, title words in any language, the box against the real-size table, pivot, units, M8-M10 quality, face count, duplicates by box, faces and material colours). `removed` / `fix` are decided by code; `removed?` / `fix?` / `keep?` are the expected outcomes once the vision check has answered; `vision?` = no title evidence (generated models, titles naming no type): two vision passes decide.

## Totals

| status | models |
|---|---|
| keep? | 653 |
| fix? | 28 |
| vision? | 273 |
| removed? | 11 |
| removed | 101 |

## Per source

| source | keep? | fix? | vision? | removed? | removed | total |
|---|---|---|---|---|---|---|
| abo | 513 | 4 | 8 | 0 | 13 | 538 |
| generated | 0 | 15 | 243 | 0 | 23 | 281 |
| objaverse | 110 | 7 | 21 | 11 | 64 | 213 |
| polyhaven | 30 | 2 | 1 | 0 | 1 | 34 |

## Per type

| kind | type | keep? | fix? | vision? | removed? | removed | total |
|---|---|---|---|---|---|---|---|
| furniture | bed_single | 6 | 0 | 8 | 0 | 6 | 20 |
| furniture | bed_double | 17 | 1 | 2 | 0 | 1 | 21 |
| furniture | sofa | 16 | 0 | 2 | 0 | 5 | 23 |
| furniture | armchair | 20 | 0 | 2 | 1 | 0 | 23 |
| furniture | table_dining | 21 | 0 | 0 | 2 | 0 | 23 |
| furniture | table_coffee | 20 | 0 | 0 | 1 | 2 | 23 |
| furniture | desk | 20 | 1 | 0 | 0 | 2 | 23 |
| furniture | chair | 18 | 0 | 3 | 1 | 0 | 22 |
| furniture | wardrobe | 14 | 0 | 4 | 0 | 2 | 20 |
| furniture | fridge | 1 | 0 | 14 | 2 | 2 | 19 |
| furniture | stove | 4 | 0 | 13 | 0 | 3 | 20 |
| furniture | sink_kitchen | 0 | 1 | 14 | 0 | 0 | 15 |
| furniture | washbasin | 1 | 0 | 16 | 1 | 2 | 20 |
| furniture | toilet | 3 | 3 | 8 | 0 | 5 | 19 |
| furniture | shower | 0 | 0 | 10 | 0 | 0 | 10 |
| furniture | bathtub | 0 | 0 | 5 | 0 | 15 | 20 |
| furniture | tv_unit | 21 | 0 | 1 | 0 | 0 | 22 |
| furniture | bookshelf | 21 | 1 | 0 | 1 | 0 | 23 |
| furniture | nightstand | 21 | 0 | 0 | 0 | 0 | 21 |
| furniture | dresser | 19 | 0 | 1 | 0 | 0 | 20 |
| furniture | washing_machine | 0 | 0 | 20 | 0 | 0 | 20 |
| furniture | side_table | 20 | 0 | 0 | 0 | 0 | 20 |
| furniture | floor_lamp | 14 | 0 | 2 | 0 | 4 | 20 |
| furniture | potted_plant | 5 | 0 | 14 | 0 | 1 | 20 |
| furniture | sofa_corner | 16 | 2 | 1 | 0 | 0 | 19 |
| furniture | chaise | 5 | 0 | 5 | 0 | 0 | 10 |
| furniture | ottoman | 18 | 0 | 0 | 1 | 1 | 20 |
| furniture | bench | 13 | 0 | 0 | 0 | 7 | 20 |
| furniture | bar_stool | 20 | 0 | 0 | 0 | 0 | 20 |
| furniture | office_chair | 20 | 0 | 0 | 0 | 0 | 20 |
| furniture | console_table | 15 | 0 | 5 | 0 | 0 | 20 |
| furniture | crib | 1 | 2 | 4 | 0 | 1 | 8 |
| furniture | bunk_bed | 0 | 10 | 0 | 0 | 0 | 10 |
| furniture | sideboard | 20 | 0 | 0 | 0 | 0 | 20 |
| furniture | shoe_cabinet | 12 | 3 | 5 | 0 | 0 | 20 |
| furniture | display_cabinet | 1 | 0 | 7 | 0 | 0 | 8 |
| furniture | tall_cabinet | 3 | 2 | 10 | 0 | 2 | 17 |
| decor | cushion | 18 | 0 | 0 | 0 | 3 | 21 |
| decor | rug | 20 | 0 | 0 | 0 | 0 | 20 |
| decor | wall_art | 17 | 0 | 0 | 0 | 0 | 17 |
| decor | vase | 20 | 0 | 0 | 0 | 0 | 20 |
| decor | bowl | 0 | 0 | 19 | 0 | 0 | 19 |
| decor | plant_small | 0 | 0 | 20 | 0 | 0 | 20 |
| decor | table_lamp | 20 | 0 | 0 | 0 | 0 | 20 |
| decor | mirror | 16 | 0 | 0 | 0 | 1 | 17 |
| decor | curtain | 8 | 0 | 8 | 1 | 3 | 20 |
| decor | blind | 0 | 0 | 8 | 0 | 1 | 9 |
| decor | throw | 0 | 0 | 9 | 0 | 8 | 17 |
| decor | books | 4 | 0 | 10 | 0 | 6 | 20 |
| decor | candle | 18 | 0 | 0 | 0 | 2 | 20 |
| decor | basket | 16 | 1 | 0 | 0 | 3 | 20 |
| decor | tray | 8 | 1 | 4 | 0 | 7 | 20 |
| decor | clock | 18 | 0 | 0 | 0 | 2 | 20 |
| decor | sculpture | 9 | 0 | 6 | 0 | 2 | 17 |
| decor | plant_large | 0 | 0 | 10 | 0 | 0 | 10 |
| decor | pendant_light | 17 | 0 | 1 | 0 | 2 | 20 |
| decor | ceiling_light | 15 | 0 | 2 | 0 | 0 | 17 |
| decor | plant | 3 | 0 | 0 | 0 | 0 | 3 |

## Removal reasons (a model may have several)

| reason | models |
|---|---|
| title flag | 30 |
| proportions fit no real piece | 28 |
| title names another type | 28 |
| licence not allowed | 18 |
| duplicate | 5 |

## Fixes (catalogue fields)

| fix | models |
|---|---|
| front_quarter_turns | 17 |
| rescale | 7 |

## Waiting for the vision check

| needs | models |
|---|---|
| vision: the vision check of every model | 671 |
| vision x2: generated (two vision passes) | 258 |
| vision: few faces (crude unless the vision quality is high) | 56 |
| vision x2: no title evidence (two vision passes) | 36 |
| vision: retype (title and vision) | 4 |
| vision: title flag | 3 |

## Models to remove (catalogue only; the files stay on the volume)

| id | type | source | status | reason | title |
|---|---|---|---|---|---|
| gen_bed_single_classic_1_dbac0f10 | bed_single | generated | removed | proportions 1.19 x 1.68 x 1.08 m fit no real bed_single (width (0.8, 1.2), depth (1.8, 2.2), height (0.25, 1.6)) | Generated classic bed single (1) |
| gen_bed_single_japandi_1_35dff430 | bed_single | generated | removed | proportions 1.26 x 1.59 x 0.67 m fit no real bed_single (width (0.8, 1.2), depth (1.8, 2.2), height (0.25, 1.6)) | Generated japandi bed single (1) |
| gen_bed_single_mediterranean_1_c9d313b4 | bed_single | generated | removed | proportions 1.21 x 1.65 x 0.86 m fit no real bed_single (width (0.8, 1.2), depth (1.8, 2.2), height (0.25, 1.6)) | Generated mediterranean bed single (1) |
| gen_bed_single_modern_minimal_1_5c05505b | bed_single | generated | removed | proportions 1.29 x 1.57 x 0.75 m fit no real bed_single (width (0.8, 1.2), depth (1.8, 2.2), height (0.25, 1.6)) | Generated modern minimal bed single (1) |
| gen_bed_single_scandinavian_1_8060783a | bed_single | generated | removed | proportions 1.24 x 1.62 x 0.72 m fit no real bed_single (width (0.8, 1.2), depth (1.8, 2.2), height (0.25, 1.6)) | Generated scandinavian bed single (1) |
| objaverse_6eb4212e70b941a3bd2db196a47828b9 | bed_single | objaverse | removed | the title says lowpoly: not photoreal | Lowpoly Bed |
| abo_B01N6AQX0A | bed_double | abo | removed | the title says luchtbed: not the object | Intex Premaire Luchtbed met Fiber Tech-technologie, nieuwe g |
| abo_B07HZ5P7P9 | sofa | abo | removed | the title says sectional component: a part of a piece | Amazon Brand – Stone & Beam Bagley Sectional Component, Left |
| abo_B07HZ6GJC2 | sofa | abo | removed | the title says sectional component: a part of a piece | Amazon Brand – Stone & Beam Bagley Sectional Component, Righ |
| abo_B07HZ6HHFF | sofa | abo | removed | the title says sectional component: a part of a piece | Amazon Brand – Stone & Beam Bagley Sectional Component, Arml |
| abo_B07HZ6X7ZF | sofa | abo | removed | the title says sectional component: a part of a piece | Amazon Brand – Stone & Beam Bagley Sectional Component, Left |
| abo_B07HZ72L2H | sofa | abo | removed | the title says sectional component: a part of a piece | Amazon Brand – Stone & Beam Bagley Sectional Component, Righ |
| objaverse_124297e7e4574c48b9c1b814b6ddf516 | armchair | objaverse | removed? | 2086 triangles (< 3000): crude unless the vision quality is high | animated_sphere |
| objaverse_3b4ee19c627e4fb4a3305621cf925aa2 | table_dining | objaverse | removed? | the title says dining set: several objects (a set or a scene) | Dining Set |
| objaverse_724d93a7f3644f96909e8c55909c6418 | table_dining | objaverse | removed? | the title says table chairs: several objects (a set or a scene) | A table, chairs & few cups |
| abo_B072ZK2FZ6 | table_coffee | abo | removed | proportions 0.80 x 0.36 x 0.58 m fit no real table_coffee (width (0.6, 1.4), depth (0.4, 1.2), height (0.25, 0.6)) | Amazon Brand – Rivet Industrial Modern Wood and Metal Coffee |
| objaverse_956a47ccc1a54a40a8711f3852d54433 | table_coffee | objaverse | removed? | 2800 triangles (< 3000): crude unless the vision quality is high | 55555 |
| objaverse_bbe1d47c0d714884a66c53d6c1e5d177 | table_coffee | objaverse | removed | the title names mesa comedor, not a table_coffee | MESA COMEDOR |
| objaverse_1b256f6ce7924f59a756fe8f7ba69416 | desk | objaverse | removed | the title says test: not photoreal | FF Desk Drawer 3D Test 5 Obj |
| objaverse_cb43e2abac66494d81e1e7116eb47043 | chair | objaverse | removed? | 2560 triangles (< 3000): crude unless the vision quality is high | Vintage Chair |
| objaverse_094697a23146463cb5564ac8bf89e5c4 | wardrobe | objaverse | removed | licence CC-BY-NC-4.0 not allowed (user decision of 10 Oct 2026) | Traditional Mennonite corner cabinet |
| objaverse_b46803ba0bc64e12b31f832fb761c4e0 | wardrobe | objaverse | removed | the title names shelf, not a wardrobe | Simple Tall Shelf |
| objaverse_2071bda681b642218b6829b82e4fd93b | fridge | objaverse | removed? | 2096 triangles (< 3000): crude unless the vision quality is high | Refrigerator - Grey Polished Metal |
| objaverse_68d69bbf7a454a09a2536ac0762532f3 | fridge | objaverse | removed? | 2074 triangles (< 3000): crude unless the vision quality is high | Old Fridge |
| objaverse_c9c4e705bf794cb88d5d8726095f4917 | fridge | objaverse | removed | licence CC-BY-NC-4.0 not allowed (user decision of 10 Oct 2026) | Haier Refrigerator |
| objaverse_f32ec9229a8749d1b79245813fbd6c31 | fridge | objaverse | removed | the title says stylized: not photoreal | Stylized Fridge |
| gen_stove_modern_minimal_1_18c4c83a | stove | generated | removed | proportions 0.94 x 0.77 x 0.80 m fit no real stove (width (0.45, 0.95), depth (0.5, 0.7), height (0.8, 1.2)) | Generated modern minimal stove (1) |
| gen_stove_scandinavian_2_4aebb9bc | stove | generated | removed | proportions 1.00 x 0.80 x 0.80 m fit no real stove (width (0.45, 0.95), depth (0.5, 0.7), height (0.8, 1.2)) | Generated scandinavian stove (2) |
| gen_stove_scandinavian_4_c71c9213 | stove | generated | removed | proportions 1.03 x 0.73 x 0.80 m fit no real stove (width (0.45, 0.95), depth (0.5, 0.7), height (0.8, 1.2)) | Generated scandinavian stove (4) |
| objaverse_3eafb89804b54c8e8cbe35e4d456e0a9 | washbasin | objaverse | removed | licence CC-BY-SA-4.0 not allowed (user decision of 10 Oct 2026) | Bathroom |
| objaverse_493b70a6177d4a1385b6b0ce041a93b0 | washbasin | objaverse | removed? | 1070 triangles (< 3000): crude unless the vision quality is high | same sink but less sanitary |
| objaverse_f76c502218884914a27148f656a9b656 | washbasin | objaverse | removed | the title names bathroom, not a washbasin | Bathroom1 |
| objaverse_1bd73c9a74d14ce29e45c277570990e6 | toilet | objaverse | removed | licence CC-BY-SA-4.0 not allowed (user decision of 10 Oct 2026) | Zenit Close Coupled Push Button Flush Toilet |
| objaverse_4398bcb5976945b08f195816340247b8 | toilet | objaverse | removed | licence CC-BY-SA-4.0 not allowed (user decision of 10 Oct 2026) | Memoirs Stately Close Coupled Toilet |
| objaverse_5b18711616054a44b025d9272b745a6a | toilet | objaverse | removed | the title says low poly: not photoreal | Qualitas Bathrooms toilet low poly |
| objaverse_bd0f8d2bfba24376bec2b827a0cbbabe | toilet | objaverse | removed | licence CC-BY-NC-4.0 not allowed (user decision of 10 Oct 2026) | CWLCCST1-6DT01 Ld |
| objaverse_c901dfa120a0487a9f5c9a2d241f70ab | toilet | objaverse | removed | the title says low poly: not photoreal | Animated low poly toilet |
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
| objaverse_4939d1bca386405f9cc22c48441b63de | bookshelf | objaverse | removed? | 2008 triangles (< 3000): crude unless the vision quality is high | Bookcase |
| objaverse_01c53767c1f84f55ad9f46eb89949cf9 | floor_lamp | objaverse | removed | the title says street lamp: an outdoor piece | Street Lamp |
| objaverse_0a34dc814a3a44cfa76388e732c05376 | floor_lamp | objaverse | removed | the title says lamppost: an outdoor piece | Lamppost |
| objaverse_53409613b45b42b98b979f12ab8faa12 | floor_lamp | objaverse | removed | the title says low poly: not photoreal | low poly Lamp 3d model |
| objaverse_71853da424aa4b208e14f6cf430339ae | floor_lamp | objaverse | removed | the title says street light: an outdoor piece | Street lights |
| objaverse_41e58efcf647494483f9860df99acf60 | potted_plant | objaverse | removed | the title names empty flower pot, not a potted_plant | Empty Flower Pot |
| objaverse_34fe7fd87a924cf8aeff89ea6f012bae | ottoman | objaverse | removed? | 2752 triangles (< 3000): crude unless the vision quality is high | Wooden stool |
| objaverse_c4304814dcc441b4a6ebb5cf99081ffe | ottoman | objaverse | removed | licence CC-BY-NC-SA-4.0 not allowed (user decision of 10 Oct 2026) | Decor, footrest |
| objaverse_36dc07c8e85c4b859d78ccd4dd60c63d | bench | objaverse | removed | the title says park bench: an outdoor piece | បង់អង្គុយសាធារណះ - Park Bench |
| objaverse_378cd6e6f505493aa8e22f68db1cabec | bench | objaverse | removed | the title says park bench: an outdoor piece | Simple Park Bench |
| objaverse_7a0c2a659e2441b6b568a9d2acf8419e | bench | objaverse | removed | the title says park bench: an outdoor piece | Park Bench |
| objaverse_83bb7dff14e84ecbbc99ebb80fe2977c | bench | objaverse | removed | licence CC-BY-SA-4.0 not allowed (user decision of 10 Oct 2026) | City Bench 001 |
| objaverse_9a4d1c954ed446d9a8d436d5be6dedca | bench | objaverse | removed | licence CC-BY-NC-SA-4.0 not allowed (user decision of 10 Oct 2026) | Mainstreet USA Bench |
| objaverse_da39bc3a29364f8bb4bf45bccf856bdc | bench | objaverse | removed | the title says gardens: an outdoor piece | Dedicated Bench, Museum Gardens, E2. (Raw Scan) |
| objaverse_f889c3adfc5945dcb10c1a594b35957b | bench | objaverse | removed | licence CC-BY-NC-4.0 not allowed (user decision of 10 Oct 2026) | Street Wooden Bench |
| objaverse_dbb8dec952c0450ba58fb4f75abf86ec | crib | objaverse | removed | proportions 1.06 x 0.60 x 1.30 m fit no real crib (width (1.15, 1.5), depth (0.6, 0.85), height (0.7, 1.3)) | Cot Final |
| abo_B07H8VCDWP | tall_cabinet | abo | removed | the title names aparador, vitrina, not a tall_cabinet | Marca Amazon - Movian Moselle - Aparador con vitrina (roble  |
| abo_B07LC9HXSF | tall_cabinet | abo | removed | the title names dressing table, not a tall_cabinet | Amazon Brand - Solimo Polaris Engineered Wood Dressing Table |
| abo_B079V6V6TF | cushion | abo | removed | a copy of abo_B079TXJNJD (box +-1 cm, faces +-1%, same texture) | Amazon Brand – Rivet Modern Geometric Decorative Print Pillo |
| abo_B07BMTNH22 | cushion | abo | removed | a copy of abo_B07BMT4F21 (box +-1 cm, faces +-1%, same texture) | Amazon Brand – Rivet Modern Abstract Geometric Decorative Th |
| abo_B07C8MT64T | cushion | abo | removed | a copy of abo_B07BMTXHSR (box +-1 cm, faces +-1%, same texture) | Amazon Brand – Rivet Modern Mosaic Throw Pillow - 20 x 20 In |
| abo_B07RNMNFQ5 | mirror | abo | removed | a copy of abo_B07RNMMYPR (box +-1 cm, faces +-1%, same texture) | Amazon Basics Rectangular Wall Mirror 30" x 40" - Standard T |
| objaverse_5b9e03a46de84bd58d3894cab9f40a78 | curtain | objaverse | removed | the title names window, not a curtain | Window |
| objaverse_87f2d57d6d7e4f22b2ac2da367dd6007 | curtain | objaverse | removed? | the title says scene: several objects (a set or a scene) | Scene |
| objaverse_dac09c92cc82445994d76c1083ca8888 | curtain | objaverse | removed | the title names window, not a curtain | Window |
| objaverse_e826c513779149d7ab3bde944647573f | curtain | objaverse | removed | the title names window, not a curtain | Window |
| gen_blind_scandinavian_1_f05a9bbd | blind | generated | removed | proportions 0.42 x 0.40 x 0.43 m fit no real blind (width (0.3, 3.0), depth (0.01, 0.35), height (0.4, 3.0)) | Generated scandinavian blind (1) |
| objaverse_0039218299e647d788844de8e1ef7cc2 | throw | objaverse | removed | the title says linnamagi: not the object | Ehavere linnamägi (Estonia) |
| objaverse_0d5590d1d2184aa98797c3d6382afd7e | throw | objaverse | removed | the title names futon, bed, not a throw | Japanese futon/bed |
| objaverse_2fbb8f56b1ba47bdb6746d95b6fc2242 | throw | objaverse | removed | the title names towel, not a throw | Hanging Towel |
| objaverse_68ba20aeb8fe4a03befaa2db5b429758 | throw | objaverse | removed | the title names kitty, not a throw | Comfy kitty |
| objaverse_6b46b33bdff44269bf9391774bb8dd63 | throw | objaverse | removed | the title names machine, not a throw | JuiceMachine |
| objaverse_be9b034525c246cebab3620acb5a8027 | throw | objaverse | removed | the title says corpse: not the object | Corpse |
| objaverse_eee70cb7980a4ca7aa0a2f86c492283e | throw | objaverse | removed | the title names bench, not a throw | Bench with Cloth |
| objaverse_fcff1bddc64c4c9e98f85ff848a8a0eb | throw | objaverse | removed | the title names bench, not a throw | Saoura Traditional bench |
| objaverse_1c77a05af556408dbfa04ad1999a8a32 | books | objaverse | removed | licence CC-BY-SA-4.0 not allowed (user decision of 10 Oct 2026) | Books |
| objaverse_36ef9c80cceb48909e11b358aee00223 | books | objaverse | removed | licence CC-BY-NC-SA-4.0 not allowed (user decision of 10 Oct 2026) | Book |
| objaverse_6931e14a96f64b158ac4cebcf7ae8763 | books | objaverse | removed | licence CC-BY-SA-4.0 not allowed (user decision of 10 Oct 2026) | Opened comics book |
| objaverse_775a10863f4b4819a409788ad183e2d5 | books | objaverse | removed | licence CC-BY-NC-SA-4.0 not allowed (user decision of 10 Oct 2026) | Box on Ready Player Two |
| objaverse_dfcd6f9d7aba46938912a0f68d0ce676 | books | objaverse | removed | licence CC-BY-NC-SA-4.0 not allowed (user decision of 10 Oct 2026) | The Woodbook #3DST29 |
| objaverse_f8052beda9344eba88c5692c6a29a2cf | books | objaverse | removed | the title names box, not a books | Exclusive Kickstarter DELUXE Box |
| objaverse_c532273884b0455b8e65664bbb91f4c4 | candle | objaverse | removed | licence CC-BY-NC-4.0 not allowed (user decision of 10 Oct 2026) | Medieval candle |
| objaverse_c5b1ca5b8492426199932f6b1a64a4d9 | candle | objaverse | removed | the title says lowpoly: not photoreal | Lowpoly Candle |
| objaverse_01c77468a1d04414ae24ecd1d1559f7d | basket | objaverse | removed | the title says stylized: not photoreal | Stylized Sand Bricks Material |
| objaverse_7f39b77440c4416cab9dbba79f3262a2 | basket | objaverse | removed | the title names bowl, not a basket | Terracotta Bowl |
| objaverse_be0b7e93e66a4d4c84c2d0a13fe1852a | basket | objaverse | removed | a copy of objaverse_bb7e9cf4496f420c8d825d2e507f124b (box +-1 cm, faces +-1%, same texture) | Bread In Basket |
| objaverse_085dca6d7eaa49a2bc459adfe3357da9 | tray | objaverse | removed | the title names shelf, not a tray | SIMPLE Shelf |
| objaverse_3dc49a977873417088384f5ae78c5a6c | tray | objaverse | removed | the title names bento, not a tray | Unagyu-bento |
| objaverse_3ed0c8a70da84ee99816fa29e352ac16 | tray | objaverse | removed | the title names couch, not a tray | Low Poly Couch |
| objaverse_545d37a90a7d4c00b5e5bc551c71fbbf | tray | objaverse | removed | the title names светильник, not a tray | Светильник DL303-L7W Maytoni |
| objaverse_8c63e5e160064cd3862e4b5f8781032b | tray | objaverse | removed | the title names светильник, not a tray | Светильник DL303-L12W Maytoni /40 |
| objaverse_985b48efbd774f8f9fa74304508cad34 | tray | objaverse | removed | the title names sink, not a tray | FRUTTI GIALLI - SQUARE SINK FROM ITALY |
| objaverse_c1e6ac573c37485f9e7acaaae418df30 | tray | objaverse | removed | the title names cutting board, not a tray | Cutting board |
| objaverse_01fb2f80dad74a2280a4c077d871b262 | clock | objaverse | removed | the title names grandfather clock, not a clock | Grandfather Clock |
| objaverse_dfe6f89d65be4a23b28abf07178efebf | clock | objaverse | removed | the title says galvanometer: not the object | Western Electric Tangent Galvanometer |
| objaverse_36bb9a6e62ab4b88b7154c41489b5f41 | sculpture | objaverse | removed | the title says low poly: not photoreal | Fountain - low-poly |
| objaverse_bac9ee64eb454a66a637ae0c20f56364 | sculpture | objaverse | removed | the title says cemiterio: an outdoor piece | Anjo de Cemitério/ Angel Cemitery |
| objaverse_069fe37a0f144d8387db9b4594c501af | pendant_light | objaverse | removed | the title names wall sconce, not a pendant_light | Copper wall sconce |
| objaverse_600a996f3b9e44fd912beb8129b5f929 | pendant_light | objaverse | removed | licence CC-BY-NC-4.0 not allowed (user decision of 10 Oct 2026) | Small Chandelier |
| WoodenTable_01 | desk | polyhaven | removed | proportions 1.80 x 0.66 x 0.55 m fit no real desk (width (0.9, 2.0), depth (0.5, 0.9), height (0.65, 1.2)) | Wooden Table 01 |

## Models to fix

| id | type | source | fixes | why |
|---|---|---|---|---|
| objaverse_08f7f65edfea417b8ed9ca748381e507 | bed_double | objaverse | {"rescale": 0.8483} | the unit guess put it 18% off a real bed_double: rescaled x0.848; units guessed (x0.001) |
| gen_sink_kitchen_scandinavian_1_dbad65c6 | sink_kitchen | generated | {"front_quarter_turns": 3} | generated (TRELLIS.2): no real product; its front is on the wrong side for a sink_kitchen (width along the front): turne |
| gen_toilet_mediterranean_1_09b9f7e2 | toilet | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; its front is on the wrong side for a toilet (width along the front): turned 90 d |
| gen_toilet_minimal_1_3799392b | toilet | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; its front is on the wrong side for a toilet (width along the front): turned 90 d |
| gen_toilet_scandinavian_6_b1b3db93 | toilet | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; its front is on the wrong side for a toilet (width along the front): turned 90 d |
| abo_B07B4FZXK2 | sofa_corner | abo | {"front_quarter_turns": 1} | its front is on the wrong side for a sofa_corner (width along the front): turned 90 deg (to the geometric front +X); the |
| abo_B07BW8MJQT | sofa_corner | abo | {"front_quarter_turns": 3} | its front is on the wrong side for a sofa_corner (width along the front): turned 270 deg (to the geometric front -X); th |
| gen_crib_classic_4_d4e08139 | crib | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; its front is on the wrong side for a crib (width along the front): turned 90 deg |
| gen_crib_mediterranean_4_d3d32233 | crib | generated | {"rescale": 1.1669} | generated (TRELLIS.2): no real product; the unit guess put it 17% off a real crib: rescaled x1.167 |
| gen_bunk_bed_industrial_4_a364b7d0 | bunk_bed | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; its front is on the wrong side for a bunk_bed (width along the front): turned 90 |
| gen_bunk_bed_mediterranean_1_d9f8e70f | bunk_bed | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; its front is on the wrong side for a bunk_bed (width along the front): turned 90 |
| gen_bunk_bed_mediterranean_4_b3b0eca5 | bunk_bed | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; its front is on the wrong side for a bunk_bed (width along the front): turned 90 |
| gen_bunk_bed_minimal_3_209e481a | bunk_bed | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; its front is on the wrong side for a bunk_bed (width along the front): turned 90 |
| gen_bunk_bed_modern_minimal_3_d55e3538 | bunk_bed | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; its front is on the wrong side for a bunk_bed (width along the front): turned 90 |
| gen_bunk_bed_rustic_4_c03d21d4 | bunk_bed | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2): no real product; its front is on the wrong side for a bunk_bed (width along the front): turned 90 |
| objaverse_1ab0499f7a7746188eefe85c1f16594b | bunk_bed | objaverse | {"front_quarter_turns": 1} | its front is on the wrong side for a bunk_bed (width along the front): turned 90 deg (side unknown: the vision check con |
| objaverse_7ea465a1489c4b12bb5a8ff33325cccb | bunk_bed | objaverse | {"front_quarter_turns": 1} | its front is on the wrong side for a bunk_bed (width along the front): turned 90 deg (side unknown: the vision check con |
| objaverse_c505ffffc1524865ba63af837346f1f7 | bunk_bed | objaverse | {"front_quarter_turns": 1} | the title names a near type (double bed); its front is on the wrong side for a bunk_bed (width along the front): turned  |
| objaverse_ea40259ea9ab488e8fe21eaf2fc29d6e | bunk_bed | objaverse | {"front_quarter_turns": 1} | its front is on the wrong side for a bunk_bed (width along the front): turned 90 deg (side unknown: the vision check con |
| gen_shoe_cabinet_industrial_3_596e817a | shoe_cabinet | generated | {"rescale": 0.8162} | generated (TRELLIS.2): no real product; the unit guess put it 23% off a real shoe_cabinet: rescaled x0.816 |
| gen_shoe_cabinet_mediterranean_1_5b538be0 | shoe_cabinet | generated | {"rescale": 0.7739} | generated (TRELLIS.2): no real product; the unit guess put it 29% off a real shoe_cabinet: rescaled x0.774 |
| gen_shoe_cabinet_mediterranean_3_4228c675 | shoe_cabinet | generated | {"rescale": 0.8228} | generated (TRELLIS.2): no real product; the unit guess put it 22% off a real shoe_cabinet: rescaled x0.823 |
| abo_B07JGPKSCB | tall_cabinet | abo | {} | the title names armoire, miroir: a wardrobe, not a tall_cabinet (retype if the vision check agrees); every model needs t |
| abo_B07JH147WS | tall_cabinet | abo | {} | the title names armadio: a wardrobe, not a tall_cabinet (retype if the vision check agrees); every model needs the visio |
| objaverse_0cd51caee3e14b2d92efaef53c7c0196 | basket | objaverse | {} | units guessed (x0.001) |
| objaverse_74c95870e2a141a9903815715d25b8a7 | tray | objaverse | {} | units unknown: scaled to a typical footprint of the type (normalised) |
| SchoolDesk_01 | desk | polyhaven | {"rescale": 1.2276} | it is 23% off a real desk: rescaled x1.228 |
| wooden_bookshelf_worn | bookshelf | polyhaven | {"rescale": 0.7974} | it is 25% off a real bookshelf: rescaled x0.797 |
