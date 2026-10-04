# Furniture fit report: building_fitted

Project: synthetic-06; 11 pieces, 9 library fits, 2 parametric fallbacks. Non-uniform scale cap 15 %. Footprints, types, rotations, rooms and statuses are as in the building JSON (fitting never changes them).

| piece | room | type | source | status | footprint w x d (m) | method | asset | licence | scale x / y / z | aspect err | height (m) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| f_L0_001 | r_L0_master_bed_room | bed_double | from_documents | verified | 2.03 x 1.52 | parametric | parametric:bed_double | n/a | 1.000 / 1.000 / 1.000 | - | 1.00 |
| f_L0_002 | r_L0_living_room | sofa | from_documents | verified | 2.13 x 0.91 | library | objaverse_42da0122f2134a189767d0911b401c1c | CC-BY-4.0 | 0.988 / 1.017 / 1.002 | 0.028 | 0.71 |
| f_L0_003 | r_L0_kitchen | table_dining | from_documents | verified | 1.83 x 0.91 | library | painted_wooden_table | CC0 | 0.760 / 0.804 / 0.782 | 0.056 | 0.75 |
| f_L0_004 | r_L0_bath | toilet | from_documents | verified | 0.71 x 0.51 | parametric | parametric:toilet | n/a | 1.000 / 1.000 / 1.000 | - | 0.80 |
| f_L0_005 | r_L0_kitchen | chair | from_documents | verified | 0.46 x 0.46 | library | objaverse_d2785b57e7da45858f2fe8bf4dedd68d | CC-BY-4.0 | 0.885 / 0.909 / 0.897 | 0.027 | 0.74 |
| f_L0_006 | r_L0_kitchen | chair | from_documents | verified | 0.46 x 0.46 | library | objaverse_d2785b57e7da45858f2fe8bf4dedd68d | CC-BY-4.0 | 0.885 / 0.909 / 0.897 | 0.027 | 0.74 |
| f_L0_007 | r_L0_kitchen | chair | from_documents | verified | 0.46 x 0.46 | library | objaverse_d2785b57e7da45858f2fe8bf4dedd68d | CC-BY-4.0 | 0.885 / 0.909 / 0.897 | 0.027 | 0.74 |
| f_L0_008 | r_L0_kitchen | chair | from_documents | verified | 0.46 x 0.46 | library | objaverse_d2785b57e7da45858f2fe8bf4dedd68d | CC-BY-4.0 | 0.885 / 0.909 / 0.897 | 0.027 | 0.74 |
| f_L0_009 | r_L0_kitchen | chair | from_documents | verified | 0.46 x 0.46 | library | objaverse_d2785b57e7da45858f2fe8bf4dedd68d | CC-BY-4.0 | 0.885 / 0.909 / 0.897 | 0.027 | 0.74 |
| f_L0_010 | r_L0_kitchen | chair | from_documents | verified | 0.46 x 0.46 | library | objaverse_d2785b57e7da45858f2fe8bf4dedd68d | CC-BY-4.0 | 0.885 / 0.909 / 0.897 | 0.027 | 0.74 |
| f_L0_011 | r_L0_bath | washbasin | from_documents | verified | 0.51 x 0.41 | library | objaverse_ce1a06f7cbe1425099a145f851fc5dee | CC-BY-4.0 | 0.783 / 0.854 / 0.819 | 0.086 | 0.45 |

## Parametric fallbacks

- f_L0_001 (bed_double): no bed_double candidate within 15 % non-uniform scale and 0.75..1.3 mean scale (closest: objaverse_08f7f65edfea417b8ed9ca748381e507 at 16.6 % non-uniform, mean scale 0.7773)
- f_L0_004 (toilet): no toilet candidate within 15 % non-uniform scale and 0.75..1.3 mean scale (closest: objaverse_0b3325fad3e740b1ac86173c90b56afd at 88.0 % non-uniform, mean scale 1.1786)

## Library assets and licences

- objaverse_42da0122f2134a189767d0911b401c1c (objaverse, CC-BY-4.0) x 1
- objaverse_ce1a06f7cbe1425099a145f851fc5dee (objaverse, CC-BY-4.0) x 1
- objaverse_d2785b57e7da45858f2fe8bf4dedd68d (objaverse, CC-BY-4.0) x 6
- painted_wooden_table (polyhaven, CC0) x 1

## Attribution (CC BY 4.0)

- objaverse_42da0122f2134a189767d0911b401c1c: "Couch Gameready" by elijahorama (https://sketchfab.com/3d-models/42da0122f2134a189767d0911b401c1c), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- objaverse_ce1a06f7cbe1425099a145f851fc5dee: "Sink" by Shining Salt (https://sketchfab.com/3d-models/ce1a06f7cbe1425099a145f851fc5dee), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- objaverse_d2785b57e7da45858f2fe8bf4dedd68d: "Chair" by 杭州维界科技有限公司 (https://sketchfab.com/3d-models/d2785b57e7da45858f2fe8bf4dedd68d), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
