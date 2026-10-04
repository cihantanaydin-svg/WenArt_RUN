# Furniture fit report: building_fitted

Project: synthetic-01; 13 pieces, 12 library fits, 1 parametric fallbacks. Non-uniform scale cap 15 %. Footprints, types, rotations, rooms and statuses are as in the building JSON (fitting never changes them).

| piece | room | type | source | status | footprint w x d (m) | method | asset | licence | scale x / y / z | aspect err | height (m) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| f_L0_001 | r_L0_salon | sofa | from_documents | verified | 2.20 x 0.90 | library | abo_B072555T67 | CC-BY-4.0 | 1.050 / 1.060 / 1.055 | 0.009 | 0.84 |
| f_L0_002 | r_L0_salon | table_coffee | from_documents | verified | 1.00 x 0.60 | library | abo_B07L8DT2XT | CC-BY-4.0 | 0.937 / 0.984 / 0.961 | 0.049 | 0.44 |
| f_L0_003 | r_L0_salon | tv_unit | from_documents | verified | 1.60 x 0.45 | library | abo_B07BVHKPFS | CC-BY-4.0 | 0.984 / 0.936 / 0.960 | 0.049 | 0.59 |
| f_L0_004 | r_L0_salon | armchair | from_documents | verified | 0.90 x 0.90 | library | abo_B075X4N3GM | CC-BY-4.0 | 0.970 / 1.067 / 1.018 | 0.096 | 0.79 |
| f_L0_005 | r_L0_salon | bookshelf | from_documents | verified | 1.00 x 0.35 | library | wooden_display_shelves_01 | CC0 | 0.928 / 0.942 / 0.935 | 0.015 | 1.46 |
| f_L0_006 | r_L0_yatak_odasi | bed_double | from_documents | verified | 1.60 x 2.00 | library | abo_B071FJR4FW | CC-BY-4.0 | 0.983 / 0.948 / 0.965 | 0.036 | 1.37 |
| f_L0_007 | r_L0_yatak_odasi | nightstand | from_documents | verified | 0.50 x 0.40 | library | abo_B084MYDTKM | CC-BY-4.0 | 1.094 / 0.984 / 1.039 | 0.105 | 0.58 |
| f_L0_008 | r_L0_yatak_odasi | nightstand | from_documents | verified | 0.50 x 0.40 | library | abo_B084MYDTKM | CC-BY-4.0 | 1.094 / 0.984 / 1.039 | 0.105 | 0.58 |
| f_L0_009 | r_L0_yatak_odasi | wardrobe | from_documents | verified | 1.80 x 0.60 | library | abo_B07JGPKZYT | CC-BY-4.0 | 0.995 / 1.035 / 1.015 | 0.039 | 2.10 |
| f_L0_010 | r_L0_banyo | toilet | from_documents | verified | 0.40 x 0.70 | parametric | parametric:toilet | n/a | 1.000 / 1.000 / 1.000 | - | 0.80 |
| f_L0_011 | r_L0_banyo | washbasin | from_documents | verified | 0.60 x 0.45 | library | objaverse_ce1a06f7cbe1425099a145f851fc5dee | CC-BY-4.0 | 0.925 / 0.945 / 0.935 | 0.022 | 0.51 |
| f_L0_012 | r_L0_banyo | shower | from_documents | verified | 0.90 x 0.90 | library | gen_shower_scandinavian_1_0ae4a37a | generated (TRELLIS.2-4B, MIT) | 0.915 / 0.811 / 0.863 | 0.121 | 1.67 |
| f_L0_013 | r_L0_banyo | washing_machine | from_documents | verified | 0.60 x 0.60 | library | gen_washing_machine_scandinavian_2_67f28c86 | generated (TRELLIS.2-4B, MIT) | 0.957 / 0.963 / 0.960 | 0.007 | 0.80 |

## Parametric fallbacks

- f_L0_010 (toilet): no toilet candidate within 15 % non-uniform scale and 0.75..1.3 mean scale (closest: objaverse_3446229dce1f47528fa871cc7669136c at 25.0 % non-uniform, mean scale 0.9941)

## Library assets and licences

- abo_B071FJR4FW (abo, CC-BY-4.0) x 1
- abo_B072555T67 (abo, CC-BY-4.0) x 1
- abo_B075X4N3GM (abo, CC-BY-4.0) x 1
- abo_B07BVHKPFS (abo, CC-BY-4.0) x 1
- abo_B07JGPKZYT (abo, CC-BY-4.0) x 1
- abo_B07L8DT2XT (abo, CC-BY-4.0) x 1
- abo_B084MYDTKM (abo, CC-BY-4.0) x 2
- gen_shower_scandinavian_1_0ae4a37a (generated, generated (TRELLIS.2-4B, MIT)) x 1
- gen_washing_machine_scandinavian_2_67f28c86 (generated, generated (TRELLIS.2-4B, MIT)) x 1
- objaverse_ce1a06f7cbe1425099a145f851fc5dee (objaverse, CC-BY-4.0) x 1
- wooden_display_shelves_01 (polyhaven, CC0) x 1

## Ranking (fit v2)

Rule: style -> bed rule -> generated last -> real size (known units first, mean |scale - 1| in 5 % steps) -> quality (missing = 3) -> aspect error -> source (abo, polyhaven, objaverse, generated).

- f_L0_001 (sofa): abo_B072555T67 (abo), rank 1 of 1 tried: real size: mean |scale - 1| 0.055 (step 1); quality 3; aspect error 0.009; source abo
- f_L0_002 (table_coffee): abo_B07L8DT2XT (abo), rank 1 of 1 tried: real size: mean |scale - 1| 0.039 (step 0); quality 3; aspect error 0.049; source abo
- f_L0_003 (tv_unit): abo_B07BVHKPFS (abo), rank 1 of 1 tried: real size: mean |scale - 1| 0.040 (step 0); quality 3; aspect error 0.049; source abo
- f_L0_004 (armchair): abo_B075X4N3GM (abo), rank 1 of 1 tried: real size: mean |scale - 1| 0.039 (step 0); quality 3; aspect error 0.096; source abo
- f_L0_005 (bookshelf): wooden_display_shelves_01 (polyhaven), rank 1 of 1 tried: real size: mean |scale - 1| 0.065 (step 1); quality 3; aspect error 0.015; source polyhaven
- f_L0_006 (bed_double): abo_B071FJR4FW (abo), rank 1 of 1 tried: real size: mean |scale - 1| 0.035 (step 0); quality 3; aspect error 0.036; source abo
- f_L0_007 (nightstand): abo_B084MYDTKM (abo), rank 1 of 1 tried: real size: mean |scale - 1| 0.049 (step 0); quality 3; aspect error 0.105; source abo
- f_L0_008 (nightstand): abo_B084MYDTKM (abo), rank 1 of 1 tried: real size: mean |scale - 1| 0.049 (step 0); quality 3; aspect error 0.105; source abo
- f_L0_009 (wardrobe): abo_B07JGPKZYT (abo), rank 1 of 1 tried: real size: mean |scale - 1| 0.018 (step 0); quality 3; aspect error 0.039; source abo
- f_L0_011 (washbasin): objaverse_ce1a06f7cbe1425099a145f851fc5dee (objaverse), rank 1 of 1 tried: units not known (normalised by type): ranked after the real-size models; quality 3; aspect error 0.022; source objaverse
- f_L0_012 (shower): gen_shower_scandinavian_1_0ae4a37a (generated), rank 1 of 1 tried: generated: no other library model passed the caps; units not known (normalised by type): ranked after the real-size models; quality 3; aspect error 0.121; source generated
- f_L0_013 (washing_machine): gen_washing_machine_scandinavian_2_67f28c86 (generated), rank 1 of 1 tried: generated: no other library model passed the caps; units not known (normalised by type): ranked after the real-size models; quality 3; aspect error 0.007; source generated

## Attribution (CC BY 4.0)

- abo_B071FJR4FW: "Amazon Brand – Stone & Beam Glenwood Industrial Metal Accent Bed, Queen, 84.5"L, Oak" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- abo_B072555T67: "Marchio Amazon - Movian Ackan - Divano a 3 posti, 209 x 87 x 80 cm, grigio chiaro" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- abo_B075X4N3GM: "Amazon Brand – Rivet Aiden Tufted Mid-Century Modern Velvet Accent Chair, 35.4"W, Otter Grey" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- abo_B07BVHKPFS: "Amazon Brand – Rivet Bowlyn Mid-Century Modern Wood TV Media Table Stand, 64", Walnut" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- abo_B07JGPKZYT: "Amazon Brand - Movian Mira 4-Door Wardrobe with Mirrors, 181 x 207 x 58cm, Light Brown Oak-Effect" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- abo_B07L8DT2XT: "Phoenix Home Rustic Industrial Solid Wood and Steel Open Shelf Coffee Table, Brown" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- abo_B084MYDTKM: "Amazon Brand - Rivet Mango Wood and Iron 3-Drawer Shutter Nightstand, 18"W, Natural Finish" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- objaverse_ce1a06f7cbe1425099a145f851fc5dee: "Sink" by Shining Salt (https://sketchfab.com/3d-models/ce1a06f7cbe1425099a145f851fc5dee), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
