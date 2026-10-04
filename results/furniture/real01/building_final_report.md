# Furniture fit report: building_final

Project: real01; 22 pieces, 1 library fits, 21 parametric fallbacks. Non-uniform scale cap 15 %. Footprints, types, rotations, rooms and statuses are as in the building JSON (fitting never changes them).

Library style filter: family 'scandinavian' (the profile's family, outputs/real01/style.json): library models only when their styles hold 'scandinavian' or 'neutral'

| piece | room | type | source | status | footprint w x d (m) | method | asset | licence | scale x / y / z | aspect err | height (m) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| f_L0_001 | r_L0_kitchen | kitchen_counter | from_documents | verified | 0.99 x 0.61 | parametric | parametric:kitchen_counter | n/a | 1.000 / 1.000 / 1.000 | - | 0.90 |
| f_L0_002 | r_L0_kitchen | kitchen_counter | from_documents | verified | 2.57 x 0.61 | parametric | parametric:kitchen_counter | n/a | 1.000 / 1.000 / 1.000 | - | 0.90 |
| f_L0_003 | r_L0_room | stair | from_documents | verified | 2.44 x 1.53 | parametric | parametric:stair | n/a | 1.000 / 1.000 / 1.000 | - | 3.17 |
| f_L0_004 | r_L0_bed_room_2 | bed_double | from_documents | verified | 1.78 x 2.03 | parametric | parametric:bed_double | n/a | 1.000 / 1.000 / 1.000 | - | 1.00 |
| f_L0_005 | r_L0_bed_room_2 | nightstand | from_documents | verified | 0.50 x 0.49 | parametric | parametric:nightstand | n/a | 1.000 / 1.000 / 1.000 | - | 0.50 |
| f_L0_006 | r_L0_bed_room_2 | nightstand | from_documents | verified | 0.45 x 0.50 | parametric | parametric:nightstand | n/a | 1.000 / 1.000 / 1.000 | - | 0.50 |
| f_L0_007 | r_L0_bed_room | bed_double | from_documents | verified | 1.78 x 2.03 | parametric | parametric:bed_double | n/a | 1.000 / 1.000 / 1.000 | - | 1.00 |
| f_L0_008 | r_L0_bed_room | nightstand | from_documents | verified | 0.50 x 0.49 | parametric | parametric:nightstand | n/a | 1.000 / 1.000 / 1.000 | - | 0.50 |
| f_L0_009 | r_L0_bed_room | nightstand | from_documents | verified | 0.50 x 0.45 | library | side_table_01 | CC0 | 0.901 / 0.990 / 0.946 | 0.094 | 0.52 |
| f_L0_010 | r_L0_dining | table_dining | from_documents | verified | 1.24 x 0.74 | parametric | parametric:table_dining | n/a | 1.000 / 1.000 / 1.000 | - | 0.75 |
| f_L0_011 | r_L0_dining | chair | from_documents | verified | 0.38 x 0.46 | parametric | parametric:chair | n/a | 1.000 / 1.000 / 1.000 | - | 0.90 |
| f_L0_012 | r_L0_dining | chair | from_documents | verified | 0.38 x 0.46 | parametric | parametric:chair | n/a | 1.000 / 1.000 / 1.000 | - | 0.90 |
| f_L0_013 | r_L0_dining | chair | from_documents | verified | 0.38 x 0.46 | parametric | parametric:chair | n/a | 1.000 / 1.000 / 1.000 | - | 0.90 |
| f_L0_014 | r_L0_dining | chair | from_documents | verified | 0.38 x 0.46 | parametric | parametric:chair | n/a | 1.000 / 1.000 / 1.000 | - | 0.90 |
| f_L0_015 | r_L0_dining | chair | from_documents | verified | 0.38 x 0.46 | parametric | parametric:chair | n/a | 1.000 / 1.000 / 1.000 | - | 0.90 |
| f_L0_016 | r_L0_dining | chair | from_documents | verified | 0.38 x 0.46 | parametric | parametric:chair | n/a | 1.000 / 1.000 / 1.000 | - | 0.90 |
| f_L0_017 | r_L0_drawing_room | sofa | from_documents | verified | 1.89 x 0.71 | parametric | parametric:sofa | n/a | 1.000 / 1.000 / 1.000 | - | 0.85 |
| f_L0_018 | r_L0_drawing_room | unknown | from_documents | unverified | 1.90 x 0.70 | parametric | parametric:unknown | n/a | 1.000 / 1.000 / 1.000 | - | 0.80 |
| f_L0_019 | r_L0_drawing_room | table_coffee | from_documents | verified | 1.13 x 1.12 | parametric | parametric:table_coffee | n/a | 1.000 / 1.000 / 1.000 | - | 0.45 |
| f_L0_020 | r_L0_drawing_room | floor_lamp | from_documents | verified | 0.42 x 0.42 | parametric | parametric:floor_lamp | n/a | 1.000 / 1.000 / 1.000 | - | 1.60 |
| f_L0_021 | r_L0_bath_toilet | toilet | added_by_ai | verified | 0.40 x 0.70 | parametric | parametric:toilet | n/a | 1.000 / 1.000 / 1.000 | - | 1.20 |
| f_L0_022 | r_L0_bath_toilet | washbasin | added_by_ai | verified | 0.60 x 0.45 | parametric | parametric:washbasin | n/a | 1.000 / 1.000 / 1.000 | - | 1.00 |

## Parametric fallbacks

- f_L0_001 (kitchen_counter): type kitchen_counter is parametric in the catalogue
- f_L0_002 (kitchen_counter): type kitchen_counter is parametric in the catalogue
- f_L0_003 (stair): type stair is parametric in the catalogue
- f_L0_004 (bed_double): no bed_double candidate within 15 % non-uniform scale and 0.75..1.3 mean scale (closest: objaverse_08f7f65edfea417b8ed9ca748381e507 at 30.4 % non-uniform, mean scale 0.8443)
- f_L0_005 (nightstand): no nightstand candidate within 15 % non-uniform scale and 0.75..1.3 mean scale (closest: side_table_01 at 20.0 % non-uniform, mean scale 0.9914)
- f_L0_006 (nightstand): no nightstand candidate within 15 % non-uniform scale and 0.75..1.3 mean scale (closest: side_table_01 at 35.9 % non-uniform, mean scale 0.9558)
- f_L0_007 (bed_double): no bed_double candidate within 15 % non-uniform scale and 0.75..1.3 mean scale (closest: objaverse_08f7f65edfea417b8ed9ca748381e507 at 30.4 % non-uniform, mean scale 0.8443)
- f_L0_008 (nightstand): no nightstand candidate within 15 % non-uniform scale and 0.75..1.3 mean scale (closest: side_table_01 at 19.7 % non-uniform, mean scale 0.9898)
- f_L0_010 (table_dining): no table_dining candidate within 15 % non-uniform scale and 0.75..1.3 mean scale (closest: objaverse_3b4ee19c627e4fb4a3305621cf925aa2 at 58.7 % non-uniform, mean scale 0.771)
- f_L0_011 (chair): no chair candidate within 15 % non-uniform scale and 0.75..1.3 mean scale (closest: objaverse_d2785b57e7da45858f2fe8bf4dedd68d at 24.1 % non-uniform, mean scale 0.829)
- f_L0_012 (chair): no chair candidate within 15 % non-uniform scale and 0.75..1.3 mean scale (closest: objaverse_d2785b57e7da45858f2fe8bf4dedd68d at 24.1 % non-uniform, mean scale 0.829)
- f_L0_013 (chair): no chair candidate within 15 % non-uniform scale and 0.75..1.3 mean scale (closest: objaverse_d2785b57e7da45858f2fe8bf4dedd68d at 24.1 % non-uniform, mean scale 0.829)
- f_L0_014 (chair): no chair candidate within 15 % non-uniform scale and 0.75..1.3 mean scale (closest: objaverse_d2785b57e7da45858f2fe8bf4dedd68d at 25.1 % non-uniform, mean scale 0.8261)
- f_L0_015 (chair): no chair candidate within 15 % non-uniform scale and 0.75..1.3 mean scale (closest: objaverse_d2785b57e7da45858f2fe8bf4dedd68d at 24.9 % non-uniform, mean scale 0.8319)
- f_L0_016 (chair): no chair candidate within 15 % non-uniform scale and 0.75..1.3 mean scale (closest: objaverse_d2785b57e7da45858f2fe8bf4dedd68d at 25.8 % non-uniform, mean scale 0.829)
- f_L0_017 (sofa): no model for style scandinavian
- f_L0_018 (unknown): type unknown is parametric in the catalogue
- f_L0_019 (table_coffee): no table_coffee candidate within 15 % non-uniform scale and 0.75..1.3 mean scale (closest: objaverse_1d41e84fd76241e7a8929a314052269c at 42.0 % non-uniform, mean scale 1.312)
- f_L0_020 (floor_lamp): no model for style scandinavian
- f_L0_021 (toilet): no model for style scandinavian
- f_L0_022 (washbasin): no model for style scandinavian

## Library assets and licences

- side_table_01 (polyhaven, CC0) x 1

## Models not taken (mattress rule and style filter)

- f_L0_004: GothicBed_01: styles ['classic'] include neither scandinavian nor neutral
- f_L0_004: objaverse_2bd3fcc82c9f43cfb0c8cf26c7d0107c: styles ['modern minimal', 'modern'] include neither scandinavian nor neutral
- f_L0_004: objaverse_5d3a99865ac84d8a8bf06b263aa5bb55: styles ['industrial'] include neither scandinavian nor neutral
- f_L0_005: ClassicNightstand_01: styles ['classic'] include neither scandinavian nor neutral
- f_L0_005: painted_wooden_nightstand: styles ['rustic'] include neither scandinavian nor neutral
- f_L0_006: ClassicNightstand_01: styles ['classic'] include neither scandinavian nor neutral
- f_L0_006: painted_wooden_nightstand: styles ['rustic'] include neither scandinavian nor neutral
- f_L0_007: GothicBed_01: styles ['classic'] include neither scandinavian nor neutral
- f_L0_007: objaverse_2bd3fcc82c9f43cfb0c8cf26c7d0107c: styles ['modern minimal', 'modern'] include neither scandinavian nor neutral
- f_L0_007: objaverse_5d3a99865ac84d8a8bf06b263aa5bb55: styles ['industrial'] include neither scandinavian nor neutral
- f_L0_008: ClassicNightstand_01: styles ['classic'] include neither scandinavian nor neutral
- f_L0_008: painted_wooden_nightstand: styles ['rustic'] include neither scandinavian nor neutral
- f_L0_009: ClassicNightstand_01: styles ['classic'] include neither scandinavian nor neutral
- f_L0_009: painted_wooden_nightstand: styles ['rustic'] include neither scandinavian nor neutral
- f_L0_010: dining_table: styles ['rustic'] include neither scandinavian nor neutral
- f_L0_010: wooden_table_02: styles ['rustic'] include neither scandinavian nor neutral
- f_L0_010: painted_wooden_table: styles ['rustic'] include neither scandinavian nor neutral
- f_L0_010: objaverse_5847113c458f4a2483aedd663376c7de: styles ['minimal', 'modern'] include neither scandinavian nor neutral
- f_L0_010: objaverse_5f235f066a9a416fb7177496a9117ec7: styles ['modern minimal', 'modern'] include neither scandinavian nor neutral
- f_L0_011: gallinera_chair: styles ['classic', 'rustic'] include neither scandinavian nor neutral
- f_L0_011: painted_wooden_chair_02: styles ['rustic'] include neither scandinavian nor neutral
- f_L0_011: dining_chair_02: styles ['modern'] include neither scandinavian nor neutral
- f_L0_011: objaverse_039c6026571943d6ac45c6816bcc7ff1: styles ['classic'] include neither scandinavian nor neutral
- f_L0_011: objaverse_0723b35415b0462eb5c01140b6b70340: styles ['classic'] include neither scandinavian nor neutral
- f_L0_011: objaverse_9234d8196b73434684bcbb8092cc9e2a: styles ['classic'] include neither scandinavian nor neutral
- f_L0_011: objaverse_cb43e2abac66494d81e1e7116eb47043: styles ['industrial', 'rustic'] include neither scandinavian nor neutral
- f_L0_012: gallinera_chair: styles ['classic', 'rustic'] include neither scandinavian nor neutral
- f_L0_012: painted_wooden_chair_02: styles ['rustic'] include neither scandinavian nor neutral
- f_L0_012: dining_chair_02: styles ['modern'] include neither scandinavian nor neutral
- f_L0_012: objaverse_039c6026571943d6ac45c6816bcc7ff1: styles ['classic'] include neither scandinavian nor neutral
- f_L0_012: objaverse_0723b35415b0462eb5c01140b6b70340: styles ['classic'] include neither scandinavian nor neutral
- f_L0_012: objaverse_9234d8196b73434684bcbb8092cc9e2a: styles ['classic'] include neither scandinavian nor neutral
- f_L0_012: objaverse_cb43e2abac66494d81e1e7116eb47043: styles ['industrial', 'rustic'] include neither scandinavian nor neutral
- f_L0_013: gallinera_chair: styles ['classic', 'rustic'] include neither scandinavian nor neutral
- f_L0_013: painted_wooden_chair_02: styles ['rustic'] include neither scandinavian nor neutral
- f_L0_013: dining_chair_02: styles ['modern'] include neither scandinavian nor neutral
- f_L0_013: objaverse_039c6026571943d6ac45c6816bcc7ff1: styles ['classic'] include neither scandinavian nor neutral
- f_L0_013: objaverse_0723b35415b0462eb5c01140b6b70340: styles ['classic'] include neither scandinavian nor neutral
- f_L0_013: objaverse_9234d8196b73434684bcbb8092cc9e2a: styles ['classic'] include neither scandinavian nor neutral
- f_L0_013: objaverse_cb43e2abac66494d81e1e7116eb47043: styles ['industrial', 'rustic'] include neither scandinavian nor neutral
- f_L0_014: gallinera_chair: styles ['classic', 'rustic'] include neither scandinavian nor neutral
- f_L0_014: painted_wooden_chair_02: styles ['rustic'] include neither scandinavian nor neutral
- f_L0_014: dining_chair_02: styles ['modern'] include neither scandinavian nor neutral
- f_L0_014: objaverse_039c6026571943d6ac45c6816bcc7ff1: styles ['classic'] include neither scandinavian nor neutral
- f_L0_014: objaverse_0723b35415b0462eb5c01140b6b70340: styles ['classic'] include neither scandinavian nor neutral
- f_L0_014: objaverse_9234d8196b73434684bcbb8092cc9e2a: styles ['classic'] include neither scandinavian nor neutral
- f_L0_014: objaverse_cb43e2abac66494d81e1e7116eb47043: styles ['industrial', 'rustic'] include neither scandinavian nor neutral
- f_L0_015: gallinera_chair: styles ['classic', 'rustic'] include neither scandinavian nor neutral
- f_L0_015: painted_wooden_chair_02: styles ['rustic'] include neither scandinavian nor neutral
- f_L0_015: dining_chair_02: styles ['modern'] include neither scandinavian nor neutral
- f_L0_015: objaverse_039c6026571943d6ac45c6816bcc7ff1: styles ['classic'] include neither scandinavian nor neutral
- f_L0_015: objaverse_0723b35415b0462eb5c01140b6b70340: styles ['classic'] include neither scandinavian nor neutral
- f_L0_015: objaverse_9234d8196b73434684bcbb8092cc9e2a: styles ['classic'] include neither scandinavian nor neutral
- f_L0_015: objaverse_cb43e2abac66494d81e1e7116eb47043: styles ['industrial', 'rustic'] include neither scandinavian nor neutral
- f_L0_016: gallinera_chair: styles ['classic', 'rustic'] include neither scandinavian nor neutral
- f_L0_016: painted_wooden_chair_02: styles ['rustic'] include neither scandinavian nor neutral
- f_L0_016: dining_chair_02: styles ['modern'] include neither scandinavian nor neutral
- f_L0_016: objaverse_039c6026571943d6ac45c6816bcc7ff1: styles ['classic'] include neither scandinavian nor neutral
- f_L0_016: objaverse_0723b35415b0462eb5c01140b6b70340: styles ['classic'] include neither scandinavian nor neutral
- f_L0_016: objaverse_9234d8196b73434684bcbb8092cc9e2a: styles ['classic'] include neither scandinavian nor neutral
- f_L0_016: objaverse_cb43e2abac66494d81e1e7116eb47043: styles ['industrial', 'rustic'] include neither scandinavian nor neutral
- f_L0_017: sofa_02: styles ['classic'] include neither scandinavian nor neutral
- f_L0_017: Sofa_01: styles ['classic'] include neither scandinavian nor neutral
- f_L0_017: sofa_03: styles ['classic'] include neither scandinavian nor neutral
- f_L0_017: objaverse_072d0468bb97447ab1ca7e3edea25f1f: styles ['classic'] include neither scandinavian nor neutral
- f_L0_017: objaverse_42da0122f2134a189767d0911b401c1c: styles ['modern minimal', 'modern'] include neither scandinavian nor neutral
- f_L0_017: objaverse_9b1e09abe5e34d6397937ebf59901898: styles ['modern minimal', 'modern'] include neither scandinavian nor neutral
- f_L0_017: objaverse_9c242421a7c1447f941f72b57e7473e5: styles ['modern minimal', 'modern'] include neither scandinavian nor neutral
- f_L0_017: objaverse_ef3832963ab24d129ec88fd4cac4818f: styles ['modern'] include neither scandinavian nor neutral
- f_L0_019: CoffeeTable_01: styles ['classic', 'rustic'] include neither scandinavian nor neutral
- f_L0_019: modern_coffee_table_01: styles ['modern'] include neither scandinavian nor neutral
- f_L0_019: modern_coffee_table_02: styles ['modern'] include neither scandinavian nor neutral
- f_L0_019: objaverse_b0c0c9c65d06443c87391134a62e2287: styles ['japandi', 'modern minimal', 'minimal', 'modern'] include neither scandinavian nor neutral
- f_L0_019: objaverse_c17577daa87849d09960669606c0ce27: styles ['japandi', 'modern minimal', 'minimal', 'modern'] include neither scandinavian nor neutral
- f_L0_019: objaverse_c42d069236174467a2fb536f7d42d7f0: styles ['japandi', 'modern minimal', 'minimal', 'modern'] include neither scandinavian nor neutral
- f_L0_019: objaverse_f4031bb5f7e64ebca4c37d4fa5ba6e8d: styles ['classic', 'rustic'] include neither scandinavian nor neutral
- f_L0_020: objaverse_01c53767c1f84f55ad9f46eb89949cf9: styles ['classic'] include neither scandinavian nor neutral
- f_L0_020: objaverse_33eb258d9873435690254cfbb0ea46ec: styles ['modern'] include neither scandinavian nor neutral
- f_L0_020: objaverse_71853da424aa4b208e14f6cf430339ae: styles ['industrial', 'classic'] include neither scandinavian nor neutral
- f_L0_020: objaverse_8170cf1409924abc9c3fc8becccdd36e: styles ['modern'] include neither scandinavian nor neutral
- f_L0_021: objaverse_0b3325fad3e740b1ac86173c90b56afd: styles ['modern minimal', 'minimal', 'modern'] include neither scandinavian nor neutral
- f_L0_021: objaverse_24d1b493899d407780140688abae19bc: styles ['modern minimal', 'minimal', 'modern'] include neither scandinavian nor neutral
- f_L0_021: objaverse_3446229dce1f47528fa871cc7669136c: styles ['modern minimal', 'minimal', 'modern'] include neither scandinavian nor neutral
- f_L0_022: objaverse_ce1a06f7cbe1425099a145f851fc5dee: styles ['modern minimal', 'minimal', 'modern'] include neither scandinavian nor neutral

## Decor

- cushion: parametric x 6
- plant: potted_plant_02 x 2
- cushions and books are parametric by design (the catalogue pillow model lies flat)
