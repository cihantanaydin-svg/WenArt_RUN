# Furniture fit report: building_final

Project: synthetic-06; 15 pieces, 12 library fits, 3 parametric fallbacks. Non-uniform scale cap 15 %. Footprints, types, rotations, rooms and statuses are as in the building JSON (fitting never changes them).

Library style filter: family 'modern' (the profile's family, outputs/synthetic-06/style.json): library models only when their styles hold 'modern' or 'neutral'

| piece | room | type | source | status | footprint w x d (m) | method | asset | licence | scale x / y / z | aspect err | height (m) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| f_L0_001 | r_L0_master_bed_room | bed_double | from_documents | verified | 2.03 x 1.52 | parametric | parametric:bed_double | n/a | 1.000 / 1.000 / 1.000 | - | 1.00 |
| f_L0_002 | r_L0_living_room | sofa | from_documents | verified | 2.13 x 0.91 | library | objaverse_42da0122f2134a189767d0911b401c1c | CC-BY-4.0 | 0.988 / 1.017 / 1.002 | 0.028 | 0.71 |
| f_L0_003 | r_L0_kitchen | table_dining | from_documents | verified | 1.83 x 0.91 | parametric | parametric:table_dining | n/a | 1.000 / 1.000 / 1.000 | - | 0.75 |
| f_L0_004 | r_L0_bath | toilet | from_documents | verified | 0.71 x 0.51 | parametric | parametric:toilet | n/a | 1.000 / 1.000 / 1.000 | - | 0.80 |
| f_L0_005 | r_L0_kitchen | chair | from_documents | verified | 0.46 x 0.46 | library | objaverse_d2785b57e7da45858f2fe8bf4dedd68d | CC-BY-4.0 | 0.885 / 0.909 / 0.897 | 0.027 | 0.74 |
| f_L0_006 | r_L0_kitchen | chair | from_documents | verified | 0.46 x 0.46 | library | objaverse_d2785b57e7da45858f2fe8bf4dedd68d | CC-BY-4.0 | 0.885 / 0.909 / 0.897 | 0.027 | 0.74 |
| f_L0_007 | r_L0_kitchen | chair | from_documents | verified | 0.46 x 0.46 | library | objaverse_d2785b57e7da45858f2fe8bf4dedd68d | CC-BY-4.0 | 0.885 / 0.909 / 0.897 | 0.027 | 0.74 |
| f_L0_008 | r_L0_kitchen | chair | from_documents | verified | 0.46 x 0.46 | library | objaverse_d2785b57e7da45858f2fe8bf4dedd68d | CC-BY-4.0 | 0.885 / 0.909 / 0.897 | 0.027 | 0.74 |
| f_L0_009 | r_L0_kitchen | chair | from_documents | verified | 0.46 x 0.46 | library | objaverse_d2785b57e7da45858f2fe8bf4dedd68d | CC-BY-4.0 | 0.885 / 0.909 / 0.897 | 0.027 | 0.74 |
| f_L0_010 | r_L0_kitchen | chair | from_documents | verified | 0.46 x 0.46 | library | objaverse_d2785b57e7da45858f2fe8bf4dedd68d | CC-BY-4.0 | 0.885 / 0.909 / 0.897 | 0.027 | 0.74 |
| f_L0_011 | r_L0_bath | washbasin | from_documents | verified | 0.51 x 0.41 | library | objaverse_ce1a06f7cbe1425099a145f851fc5dee | CC-BY-4.0 | 0.783 / 0.854 / 0.819 | 0.086 | 0.45 |
| f_L0_012 | r_L0_lobby | chair | added_by_ai | verified | 0.50 x 0.50 | library | objaverse_d2785b57e7da45858f2fe8bf4dedd68d | CC-BY-4.0 | 0.968 / 0.994 / 0.981 | 0.027 | 0.81 |
| f_L0_013 | r_L0_bed_room | bed_double | added_by_ai | verified | 1.80 x 2.00 | library | objaverse_2bd3fcc82c9f43cfb0c8cf26c7d0107c | CC-BY-4.0 | 1.029 / 1.019 / 1.024 | 0.009 | 1.53 |
| f_L0_014 | r_L0_bed_room | nightstand | added_by_ai | verified | 0.50 x 0.40 | library | side_table_01 | CC0 | 0.909 / 0.889 / 0.899 | 0.022 | 0.50 |
| f_L0_015 | r_L0_bed_room | nightstand | added_by_ai | verified | 0.50 x 0.40 | library | side_table_01 | CC0 | 0.909 / 0.889 / 0.899 | 0.022 | 0.50 |

## Parametric fallbacks

- f_L0_001 (bed_double): no bed_double candidate within 15 % non-uniform scale and 0.75..1.3 mean scale (closest: objaverse_08f7f65edfea417b8ed9ca748381e507 at 16.6 % non-uniform, mean scale 0.7773)
- f_L0_003 (table_dining): no table_dining candidate within 15 % non-uniform scale and 0.75..1.3 mean scale (closest: objaverse_5f235f066a9a416fb7177496a9117ec7 at 26.7 % non-uniform, mean scale 0.9646)
- f_L0_004 (toilet): no toilet candidate within 15 % non-uniform scale and 0.75..1.3 mean scale (closest: objaverse_0b3325fad3e740b1ac86173c90b56afd at 88.0 % non-uniform, mean scale 1.1786)

## Library assets and licences

- objaverse_2bd3fcc82c9f43cfb0c8cf26c7d0107c (objaverse, CC-BY-4.0) x 1
- objaverse_42da0122f2134a189767d0911b401c1c (objaverse, CC-BY-4.0) x 1
- objaverse_ce1a06f7cbe1425099a145f851fc5dee (objaverse, CC-BY-4.0) x 1
- objaverse_d2785b57e7da45858f2fe8bf4dedd68d (objaverse, CC-BY-4.0) x 7
- side_table_01 (polyhaven, CC0) x 2

## Models not taken (mattress rule and style filter)

- f_L0_001: GothicBed_01: styles ['classic'] include neither modern nor neutral
- f_L0_001: objaverse_5d3a99865ac84d8a8bf06b263aa5bb55: styles ['industrial'] include neither modern nor neutral
- f_L0_002: sofa_02: styles ['classic'] include neither modern nor neutral
- f_L0_002: Sofa_01: styles ['classic'] include neither modern nor neutral
- f_L0_002: sofa_03: styles ['classic'] include neither modern nor neutral
- f_L0_002: objaverse_072d0468bb97447ab1ca7e3edea25f1f: styles ['classic'] include neither modern nor neutral
- f_L0_003: dining_table: styles ['rustic'] include neither modern nor neutral
- f_L0_003: wooden_table_02: styles ['rustic'] include neither modern nor neutral
- f_L0_003: painted_wooden_table: styles ['rustic'] include neither modern nor neutral
- f_L0_003: objaverse_724d93a7f3644f96909e8c55909c6418: styles ['scandinavian', 'rustic'] include neither modern nor neutral
- f_L0_005: gallinera_chair: styles ['classic', 'rustic'] include neither modern nor neutral
- f_L0_005: painted_wooden_chair_02: styles ['rustic'] include neither modern nor neutral
- f_L0_005: objaverse_039c6026571943d6ac45c6816bcc7ff1: styles ['classic'] include neither modern nor neutral
- f_L0_005: objaverse_0723b35415b0462eb5c01140b6b70340: styles ['classic'] include neither modern nor neutral
- f_L0_005: objaverse_9234d8196b73434684bcbb8092cc9e2a: styles ['classic'] include neither modern nor neutral
- f_L0_005: objaverse_cb43e2abac66494d81e1e7116eb47043: styles ['industrial', 'rustic'] include neither modern nor neutral
- f_L0_006: gallinera_chair: styles ['classic', 'rustic'] include neither modern nor neutral
- f_L0_006: painted_wooden_chair_02: styles ['rustic'] include neither modern nor neutral
- f_L0_006: objaverse_039c6026571943d6ac45c6816bcc7ff1: styles ['classic'] include neither modern nor neutral
- f_L0_006: objaverse_0723b35415b0462eb5c01140b6b70340: styles ['classic'] include neither modern nor neutral
- f_L0_006: objaverse_9234d8196b73434684bcbb8092cc9e2a: styles ['classic'] include neither modern nor neutral
- f_L0_006: objaverse_cb43e2abac66494d81e1e7116eb47043: styles ['industrial', 'rustic'] include neither modern nor neutral
- f_L0_007: gallinera_chair: styles ['classic', 'rustic'] include neither modern nor neutral
- f_L0_007: painted_wooden_chair_02: styles ['rustic'] include neither modern nor neutral
- f_L0_007: objaverse_039c6026571943d6ac45c6816bcc7ff1: styles ['classic'] include neither modern nor neutral
- f_L0_007: objaverse_0723b35415b0462eb5c01140b6b70340: styles ['classic'] include neither modern nor neutral
- f_L0_007: objaverse_9234d8196b73434684bcbb8092cc9e2a: styles ['classic'] include neither modern nor neutral
- f_L0_007: objaverse_cb43e2abac66494d81e1e7116eb47043: styles ['industrial', 'rustic'] include neither modern nor neutral
- f_L0_008: gallinera_chair: styles ['classic', 'rustic'] include neither modern nor neutral
- f_L0_008: painted_wooden_chair_02: styles ['rustic'] include neither modern nor neutral
- f_L0_008: objaverse_039c6026571943d6ac45c6816bcc7ff1: styles ['classic'] include neither modern nor neutral
- f_L0_008: objaverse_0723b35415b0462eb5c01140b6b70340: styles ['classic'] include neither modern nor neutral
- f_L0_008: objaverse_9234d8196b73434684bcbb8092cc9e2a: styles ['classic'] include neither modern nor neutral
- f_L0_008: objaverse_cb43e2abac66494d81e1e7116eb47043: styles ['industrial', 'rustic'] include neither modern nor neutral
- f_L0_009: gallinera_chair: styles ['classic', 'rustic'] include neither modern nor neutral
- f_L0_009: painted_wooden_chair_02: styles ['rustic'] include neither modern nor neutral
- f_L0_009: objaverse_039c6026571943d6ac45c6816bcc7ff1: styles ['classic'] include neither modern nor neutral
- f_L0_009: objaverse_0723b35415b0462eb5c01140b6b70340: styles ['classic'] include neither modern nor neutral
- f_L0_009: objaverse_9234d8196b73434684bcbb8092cc9e2a: styles ['classic'] include neither modern nor neutral
- f_L0_009: objaverse_cb43e2abac66494d81e1e7116eb47043: styles ['industrial', 'rustic'] include neither modern nor neutral
- f_L0_010: gallinera_chair: styles ['classic', 'rustic'] include neither modern nor neutral
- f_L0_010: painted_wooden_chair_02: styles ['rustic'] include neither modern nor neutral
- f_L0_010: objaverse_039c6026571943d6ac45c6816bcc7ff1: styles ['classic'] include neither modern nor neutral
- f_L0_010: objaverse_0723b35415b0462eb5c01140b6b70340: styles ['classic'] include neither modern nor neutral
- f_L0_010: objaverse_9234d8196b73434684bcbb8092cc9e2a: styles ['classic'] include neither modern nor neutral
- f_L0_010: objaverse_cb43e2abac66494d81e1e7116eb47043: styles ['industrial', 'rustic'] include neither modern nor neutral
- f_L0_012: gallinera_chair: styles ['classic', 'rustic'] include neither modern nor neutral
- f_L0_012: painted_wooden_chair_02: styles ['rustic'] include neither modern nor neutral
- f_L0_012: objaverse_039c6026571943d6ac45c6816bcc7ff1: styles ['classic'] include neither modern nor neutral
- f_L0_012: objaverse_0723b35415b0462eb5c01140b6b70340: styles ['classic'] include neither modern nor neutral
- f_L0_012: objaverse_9234d8196b73434684bcbb8092cc9e2a: styles ['classic'] include neither modern nor neutral
- f_L0_012: objaverse_cb43e2abac66494d81e1e7116eb47043: styles ['industrial', 'rustic'] include neither modern nor neutral
- f_L0_013: GothicBed_01: styles ['classic'] include neither modern nor neutral
- f_L0_013: objaverse_5d3a99865ac84d8a8bf06b263aa5bb55: styles ['industrial'] include neither modern nor neutral
- f_L0_014: ClassicNightstand_01: styles ['classic'] include neither modern nor neutral
- f_L0_014: painted_wooden_nightstand: styles ['rustic'] include neither modern nor neutral
- f_L0_015: ClassicNightstand_01: styles ['classic'] include neither modern nor neutral
- f_L0_015: painted_wooden_nightstand: styles ['rustic'] include neither modern nor neutral

## Attribution (CC BY 4.0)

- objaverse_2bd3fcc82c9f43cfb0c8cf26c7d0107c: "Bed For Vr" by olamii (https://sketchfab.com/3d-models/2bd3fcc82c9f43cfb0c8cf26c7d0107c), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- objaverse_42da0122f2134a189767d0911b401c1c: "Couch Gameready" by elijahorama (https://sketchfab.com/3d-models/42da0122f2134a189767d0911b401c1c), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- objaverse_ce1a06f7cbe1425099a145f851fc5dee: "Sink" by Shining Salt (https://sketchfab.com/3d-models/ce1a06f7cbe1425099a145f851fc5dee), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- objaverse_d2785b57e7da45858f2fe8bf4dedd68d: "Chair" by 杭州维界科技有限公司 (https://sketchfab.com/3d-models/d2785b57e7da45858f2fe8bf4dedd68d), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched

## Decor

- cushion: parametric x 6
- plant: potted_plant_02 x 3
- cushions and books are parametric by design (the catalogue pillow model lies flat)
