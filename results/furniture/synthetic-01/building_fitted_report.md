# Furniture fit report: building_fitted

Project: synthetic-01; 13 pieces, 13 library fits, 0 parametric fallbacks. Non-uniform scale cap 15 %. Footprints, types, rotations, rooms and statuses are as in the building JSON (fitting never changes them).

| piece | room | type | source | status | footprint w x d (m) | method | asset | licence | scale x / y / z | aspect err | height (m) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| f_L0_001 | r_L0_salon | sofa | from_documents | verified | 2.20 x 0.90 | library | abo_B07BWJCBY2 | CC-BY-4.0 | 1.074 / 0.954 / 1.014 | 0.119 | 0.79 |
| f_L0_002 | r_L0_salon | table_coffee | from_documents | verified | 1.00 x 0.60 | library | abo_B07GDYVV9M | CC-BY-4.0 | 0.992 / 0.998 / 0.995 | 0.005 | 0.36 |
| f_L0_003 | r_L0_salon | tv_unit | from_documents | verified | 1.60 x 0.45 | library | abo_B07B8RYY41 | CC-BY-4.0 | 0.984 / 0.997 / 0.990 | 0.013 | 0.65 |
| f_L0_004 | r_L0_salon | armchair | from_documents | verified | 0.90 x 0.90 | library | abo_B075X4N3GM | CC-BY-4.0 | 0.970 / 1.067 / 1.018 | 0.096 | 0.79 |
| f_L0_005 | r_L0_salon | bookshelf | from_documents | verified | 1.00 x 0.35 | library | wooden_display_shelves_01 | CC0 | 0.928 / 0.942 / 0.935 | 0.015 | 1.46 |
| f_L0_006 | r_L0_yatak_odasi | bed_double | from_documents | verified | 1.60 x 2.00 | library | abo_B07GFDZW5W | CC-BY-4.0 | 0.986 / 1.020 / 1.003 | 0.034 | 0.80 |
| f_L0_007 | r_L0_yatak_odasi | nightstand | from_documents | verified | 0.50 x 0.40 | library | abo_B07PX3CC31 | CC-BY-4.0 | 1.041 / 1.050 / 1.046 | 0.008 | 0.66 |
| f_L0_008 | r_L0_yatak_odasi | nightstand | from_documents | verified | 0.50 x 0.40 | library | abo_B07PX3CC31 | CC-BY-4.0 | 1.041 / 1.050 / 1.046 | 0.008 | 0.66 |
| f_L0_009 | r_L0_yatak_odasi | wardrobe | from_documents | verified | 1.80 x 0.60 | library | abo_B07JGPKZYT | CC-BY-4.0 | 0.995 / 1.035 / 1.015 | 0.039 | 2.10 |
| f_L0_010 | r_L0_banyo | toilet | from_documents | verified | 0.40 x 0.70 | library | objaverse_c901dfa120a0487a9f5c9a2d241f70ab | CC-BY-4.0 | 0.985 / 0.991 / 0.988 | 0.007 | 0.82 |
| f_L0_011 | r_L0_banyo | washbasin | from_documents | verified | 0.60 x 0.45 | library | objaverse_f76c502218884914a27148f656a9b656 | CC-BY-4.0 | 0.904 / 0.899 / 0.902 | 0.006 | 0.54 |
| f_L0_012 | r_L0_banyo | shower | from_documents | verified | 0.90 x 0.90 | library | gen_shower_scandinavian_9_7fb81c9a | generated (TRELLIS.2-4B, MIT) | 0.830 / 0.893 / 0.862 | 0.074 | 1.69 |
| f_L0_013 | r_L0_banyo | washing_machine | from_documents | verified | 0.60 x 0.60 | library | gen_washing_machine_japandi_1_f1f4def2 | generated (TRELLIS.2-4B, MIT) | 0.963 / 0.957 / 0.960 | 0.006 | 0.82 |

## Parametric fallbacks

- none

## Library assets and licences

- abo_B075X4N3GM (abo, CC-BY-4.0) x 1
- abo_B07B8RYY41 (abo, CC-BY-4.0) x 1
- abo_B07BWJCBY2 (abo, CC-BY-4.0) x 1
- abo_B07GDYVV9M (abo, CC-BY-4.0) x 1
- abo_B07GFDZW5W (abo, CC-BY-4.0) x 1
- abo_B07JGPKZYT (abo, CC-BY-4.0) x 1
- abo_B07PX3CC31 (abo, CC-BY-4.0) x 2
- gen_shower_scandinavian_9_7fb81c9a (generated, generated (TRELLIS.2-4B, MIT)) x 1
- gen_washing_machine_japandi_1_f1f4def2 (generated, generated (TRELLIS.2-4B, MIT)) x 1
- objaverse_c901dfa120a0487a9f5c9a2d241f70ab (objaverse, CC-BY-4.0) x 1
- objaverse_f76c502218884914a27148f656a9b656 (objaverse, CC-BY-4.0) x 1
- wooden_display_shelves_01 (polyhaven, CC0) x 1

## Ranking (fit v2)

Rule: style -> bed rule -> generated last -> real size (known units first, mean |scale - 1| in 5 % steps) -> quality (missing = 3) -> aspect error -> source (abo, polyhaven, objaverse, generated).

- f_L0_001 (sofa): abo_B07BWJCBY2 (abo), rank 1 of 1 tried: real size: mean |scale - 1| 0.045 (step 0); quality 3; aspect error 0.119; source abo
- f_L0_002 (table_coffee): abo_B07GDYVV9M (abo), rank 1 of 1 tried: real size: mean |scale - 1| 0.005 (step 0); quality 3; aspect error 0.005; source abo
- f_L0_003 (tv_unit): abo_B07B8RYY41 (abo), rank 1 of 1 tried: real size: mean |scale - 1| 0.010 (step 0); quality 3; aspect error 0.013; source abo
- f_L0_004 (armchair): abo_B075X4N3GM (abo), rank 1 of 1 tried: real size: mean |scale - 1| 0.039 (step 0); quality 3; aspect error 0.096; source abo
- f_L0_005 (bookshelf): wooden_display_shelves_01 (polyhaven), rank 1 of 1 tried: real size: mean |scale - 1| 0.065 (step 1); quality 3; aspect error 0.015; source polyhaven
- f_L0_006 (bed_double): abo_B07GFDZW5W (abo), rank 1 of 1 tried: real size: mean |scale - 1| 0.013 (step 0); quality 3; aspect error 0.034; source abo
- f_L0_007 (nightstand): abo_B07PX3CC31 (abo), rank 1 of 1 tried: real size: mean |scale - 1| 0.046 (step 0); quality 3; aspect error 0.008; source abo
- f_L0_008 (nightstand): abo_B07PX3CC31 (abo), rank 1 of 1 tried: real size: mean |scale - 1| 0.046 (step 0); quality 3; aspect error 0.008; source abo
- f_L0_009 (wardrobe): abo_B07JGPKZYT (abo), rank 1 of 1 tried: real size: mean |scale - 1| 0.018 (step 0); quality 3; aspect error 0.039; source abo
- f_L0_010 (toilet): objaverse_c901dfa120a0487a9f5c9a2d241f70ab (objaverse), rank 1 of 1 tried: units not known (normalised by type): ranked after the real-size models; quality 3; aspect error 0.007; source objaverse
- f_L0_011 (washbasin): objaverse_f76c502218884914a27148f656a9b656 (objaverse), rank 1 of 1 tried: units not known (normalised by type): ranked after the real-size models; quality 3; aspect error 0.006; source objaverse
- f_L0_012 (shower): gen_shower_scandinavian_9_7fb81c9a (generated), rank 1 of 1 tried: generated: no other library model passed the caps; units not known (normalised by type): ranked after the real-size models; quality 3; aspect error 0.074; source generated
- f_L0_013 (washing_machine): gen_washing_machine_japandi_1_f1f4def2 (generated), rank 1 of 1 tried: generated: no other library model passed the caps; units not known (normalised by type): ranked after the real-size models; quality 3; aspect error 0.006; source generated

## Attribution (CC BY 4.0)

- abo_B075X4N3GM: "Amazon Brand – Rivet Aiden Tufted Mid-Century Modern Velvet Accent Chair, 35.4"W, Otter Grey" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- abo_B07B8RYY41: "Amazon Brand – Stone & Beam Bruckner Casual Wood Media Table, 64"W, Brown" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- abo_B07BWJCBY2: "Amazon Brand – Stone & Beam Bradbury Chesterfield Tufted Leather Loveseat Sofa Couch, 78.7"W, Black" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- abo_B07GDYVV9M: "Amazon Brand - Rivet Triangular Coffee Table with Solid Wood Legs, 105 x 60 x 37cm, MDF with Walnut Veneer/Solid Beech Wood" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- abo_B07GFDZW5W: "Movian Havel" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- abo_B07JGPKZYT: "Amazon Brand - Movian Mira 4-Door Wardrobe with Mirrors, 181 x 207 x 58cm, Light Brown Oak-Effect" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- abo_B07PX3CC31: "AmazonBasics Classic Wood Nightstand End Table with Cabinet - Black Oak" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- objaverse_c901dfa120a0487a9f5c9a2d241f70ab: "Animated low poly toilet" by Gamedirection (https://sketchfab.com/3d-models/c901dfa120a0487a9f5c9a2d241f70ab), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- objaverse_f76c502218884914a27148f656a9b656: "Bathroom1" by neutralize (https://sketchfab.com/3d-models/f76c502218884914a27148f656a9b656), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
