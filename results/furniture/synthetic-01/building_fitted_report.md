# Furniture fit report: building_fitted

Project: synthetic-01; 13 pieces, 8 library fits, 5 parametric fallbacks. Non-uniform scale cap 15 %. Footprints, types, rotations, rooms and statuses are as in the building JSON (fitting never changes them).

| piece | room | type | source | status | footprint w x d (m) | method | asset | licence | scale x / y / z | aspect err | height (m) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| f_L0_001 | r_L0_salon | sofa | from_documents | verified | 2.20 x 0.90 | library | objaverse_42da0122f2134a189767d0911b401c1c | CC-BY-4.0 | 1.019 / 1.001 / 1.010 | 0.018 | 0.71 |
| f_L0_002 | r_L0_salon | table_coffee | from_documents | verified | 1.00 x 0.60 | library | objaverse_f4031bb5f7e64ebca4c37d4fa5ba6e8d | CC-BY-4.0 | 0.836 / 0.897 / 0.867 | 0.071 | 0.31 |
| f_L0_003 | r_L0_salon | tv_unit | from_documents | verified | 1.60 x 0.45 | parametric | parametric:tv_unit | n/a | 1.000 / 1.000 / 1.000 | - | 0.50 |
| f_L0_004 | r_L0_salon | armchair | from_documents | verified | 0.90 x 0.90 | library | objaverse_aedb9509ef9347a5b055e02deeadeff7 | CC-BY-4.0 | 0.998 / 0.998 / 0.998 | 0.001 | 0.94 |
| f_L0_005 | r_L0_salon | bookshelf | from_documents | verified | 1.00 x 0.35 | library | objaverse_51d928b33e5549898cc86cbdaf966d83 | CC-BY-4.0 | 0.836 / 0.836 / 0.836 | 0.001 | 1.67 |
| f_L0_006 | r_L0_yatak_odasi | bed_double | from_documents | verified | 1.60 x 2.00 | library | GothicBed_01 | CC0 | 1.071 / 0.980 / 1.026 | 0.088 | 1.57 |
| f_L0_007 | r_L0_yatak_odasi | nightstand | from_documents | verified | 0.50 x 0.40 | library | side_table_01 | CC0 | 0.909 / 0.889 / 0.899 | 0.022 | 0.50 |
| f_L0_008 | r_L0_yatak_odasi | nightstand | from_documents | verified | 0.50 x 0.40 | library | side_table_01 | CC0 | 0.909 / 0.889 / 0.899 | 0.022 | 0.50 |
| f_L0_009 | r_L0_yatak_odasi | wardrobe | from_documents | verified | 1.80 x 0.60 | parametric | parametric:wardrobe | n/a | 1.000 / 1.000 / 1.000 | - | 2.10 |
| f_L0_010 | r_L0_banyo | toilet | from_documents | verified | 0.40 x 0.70 | parametric | parametric:toilet | n/a | 1.000 / 1.000 / 1.000 | - | 0.80 |
| f_L0_011 | r_L0_banyo | washbasin | from_documents | verified | 0.60 x 0.45 | library | objaverse_ce1a06f7cbe1425099a145f851fc5dee | CC-BY-4.0 | 0.925 / 0.945 / 0.935 | 0.022 | 0.51 |
| f_L0_012 | r_L0_banyo | shower | from_documents | verified | 0.90 x 0.90 | parametric | parametric:shower | n/a | 1.000 / 1.000 / 1.000 | - | 2.00 |
| f_L0_013 | r_L0_banyo | washing_machine | from_documents | verified | 0.60 x 0.60 | parametric | parametric:washing_machine | n/a | 1.000 / 1.000 / 1.000 | - | 0.85 |

## Parametric fallbacks

- f_L0_003 (tv_unit): no tv_unit candidate within 15 % non-uniform scale and 0.75..1.3 mean scale (closest: modern_wooden_cabinet at 32.0 % non-uniform, mean scale 0.7606)
- f_L0_009 (wardrobe): no wardrobe candidate within 15 % non-uniform scale and 0.75..1.3 mean scale (closest: objaverse_b3a99e956be64ab6958f7f5e1895f031 at 30.9 % non-uniform, mean scale 1.2281)
- f_L0_010 (toilet): no toilet candidate within 15 % non-uniform scale and 0.75..1.3 mean scale (closest: objaverse_3446229dce1f47528fa871cc7669136c at 25.0 % non-uniform, mean scale 0.9941)
- f_L0_012 (shower): type shower is parametric in the catalogue
- f_L0_013 (washing_machine): type washing_machine is parametric in the catalogue

## Library assets and licences

- objaverse_42da0122f2134a189767d0911b401c1c (objaverse, CC-BY-4.0) x 1
- objaverse_51d928b33e5549898cc86cbdaf966d83 (objaverse, CC-BY-4.0) x 1
- objaverse_aedb9509ef9347a5b055e02deeadeff7 (objaverse, CC-BY-4.0) x 1
- objaverse_ce1a06f7cbe1425099a145f851fc5dee (objaverse, CC-BY-4.0) x 1
- objaverse_f4031bb5f7e64ebca4c37d4fa5ba6e8d (objaverse, CC-BY-4.0) x 1
- GothicBed_01 (polyhaven, CC0) x 1
- side_table_01 (polyhaven, CC0) x 2

## Attribution (CC BY 4.0)

- objaverse_42da0122f2134a189767d0911b401c1c: "Couch Gameready" by elijahorama (https://sketchfab.com/3d-models/42da0122f2134a189767d0911b401c1c), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- objaverse_51d928b33e5549898cc86cbdaf966d83: "Simple Book Shelf | [FREE] | Agustin Honnun" by Agustín Hönnun (https://sketchfab.com/3d-models/51d928b33e5549898cc86cbdaf966d83), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- objaverse_aedb9509ef9347a5b055e02deeadeff7: "Sofa" by mustafasahinfb (https://sketchfab.com/3d-models/aedb9509ef9347a5b055e02deeadeff7), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- objaverse_ce1a06f7cbe1425099a145f851fc5dee: "Sink" by Shining Salt (https://sketchfab.com/3d-models/ce1a06f7cbe1425099a145f851fc5dee), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- objaverse_f4031bb5f7e64ebca4c37d4fa5ba6e8d: "LP Table" by doplerato (https://sketchfab.com/3d-models/f4031bb5f7e64ebca4c37d4fa5ba6e8d), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
