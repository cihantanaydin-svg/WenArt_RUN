# Furniture fit report: building_fitted

Project: synthetic-07; 18 pieces, 12 library fits, 6 parametric fallbacks. Non-uniform scale cap 15 %. Footprints, types, rotations, rooms and statuses are as in the building JSON (fitting never changes them).

| piece | room | type | source | status | footprint w x d (m) | method | asset | licence | scale x / y / z | aspect err | height (m) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| f_L-1_001 | r_L-1_hol | stair | from_documents | verified | 3.00 x 1.00 | parametric | parametric:stair | n/a | 1.000 / 1.000 / 1.000 | - | 3.17 |
| f_L-1_002 | r_L-1_mutfak | fridge | from_documents | verified | 0.70 x 0.70 | library | objaverse_68d69bbf7a454a09a2536ac0762532f3 | CC-BY-4.0 | 0.965 / 1.003 / 0.984 | 0.038 | 1.07 |
| f_L-1_003 | r_L-1_mutfak | stove | from_documents | verified | 0.60 x 0.60 | library | objaverse_934716ccd00d4f6ba9555d1cea788488 | CC-BY-4.0 | 1.177 / 1.097 / 1.137 | 0.071 | 1.36 |
| f_L-1_004 | r_L-1_mutfak | kitchen_counter | from_documents | verified | 2.40 x 0.60 | parametric | parametric:kitchen_counter | n/a | 1.000 / 1.000 / 1.000 | - | 0.90 |
| f_L-1_005 | r_L-1_salon | sofa | from_documents | verified | 2.20 x 0.90 | library | abo_B07BWJCBY2 | CC-BY-4.0 | 1.074 / 0.954 / 1.014 | 0.119 | 0.79 |
| f_L-1_006 | r_L-1_mutfak | sink_kitchen | from_documents | verified | 0.80 x 0.50 | library | gen_sink_kitchen_industrial_4_3f68e743 | generated (TRELLIS.2-4B, MIT) | 0.798 / 0.838 / 0.818 | 0.049 | 0.71 |
| f_L-1b_001 | r_L-1b_hol | stair | from_documents | verified | 3.00 x 1.00 | parametric | parametric:stair | n/a | 1.000 / 1.000 / 1.000 | - | 3.17 |
| f_L-1b_002 | r_L-1b_salon_acik_mutfak | fridge | from_documents | verified | 0.70 x 0.70 | library | objaverse_68d69bbf7a454a09a2536ac0762532f3 | CC-BY-4.0 | 0.965 / 1.003 / 0.984 | 0.038 | 1.07 |
| f_L-1b_003 | r_L-1b_salon_acik_mutfak | stove | from_documents | verified | 0.60 x 0.60 | library | objaverse_934716ccd00d4f6ba9555d1cea788488 | CC-BY-4.0 | 1.177 / 1.097 / 1.137 | 0.071 | 1.36 |
| f_L-1b_004 | r_L-1b_salon_acik_mutfak | kitchen_counter | from_documents | verified | 2.40 x 0.60 | parametric | parametric:kitchen_counter | n/a | 1.000 / 1.000 / 1.000 | - | 0.90 |
| f_L-1b_005 | r_L-1b_salon_acik_mutfak | sofa | from_documents | verified | 2.20 x 0.90 | library | abo_B07BWJCBY2 | CC-BY-4.0 | 1.074 / 0.954 / 1.014 | 0.119 | 0.79 |
| f_L-1b_006 | r_L-1b_salon_acik_mutfak | sink_kitchen | from_documents | verified | 0.80 x 0.50 | library | gen_sink_kitchen_industrial_4_3f68e743 | generated (TRELLIS.2-4B, MIT) | 0.798 / 0.838 / 0.818 | 0.049 | 0.71 |
| f_L0_001 | r_L0_hol | stair | from_documents | verified | 3.00 x 1.00 | parametric | parametric:stair | n/a | 1.000 / 1.000 / 1.000 | - | 3.17 |
| f_L0_002 | r_L0_yatak_odasi | bed_double | from_documents | verified | 2.00 x 1.60 | library | objaverse_08f7f65edfea417b8ed9ca748381e507 | CC-BY-4.0 | 0.824 / 0.754 / 0.789 | 0.089 | 0.71 |
| f_L0_003 | r_L0_banyo | shower | from_documents | verified | 0.90 x 0.90 | library | gen_shower_scandinavian_9_7fb81c9a | generated (TRELLIS.2-4B, MIT) | 0.830 / 0.893 / 0.862 | 0.074 | 1.69 |
| f_L0_004 | r_L0_banyo | toilet | from_documents | verified | 0.70 x 0.40 | library | gen_toilet_minimal_1_3799392b | generated (TRELLIS.2-4B, MIT) | 0.960 / 1.017 / 0.988 | 0.058 | 0.77 |
| f_L0_005 | r_L0_banyo | washbasin | from_documents | verified | 0.60 x 0.45 | library | objaverse_f76c502218884914a27148f656a9b656 | CC-BY-4.0 | 0.904 / 0.899 / 0.902 | 0.006 | 0.54 |
| f_L1_001 | r_L1_hol | stair | from_documents | verified | 3.00 x 1.00 | parametric | parametric:stair | n/a | 1.000 / 1.000 / 1.000 | - | 3.17 |

## Parametric fallbacks

- f_L-1_001 (stair): type stair is parametric in the catalogue
- f_L-1_004 (kitchen_counter): type kitchen_counter is parametric in the catalogue
- f_L-1b_001 (stair): type stair is parametric in the catalogue
- f_L-1b_004 (kitchen_counter): type kitchen_counter is parametric in the catalogue
- f_L0_001 (stair): type stair is parametric in the catalogue
- f_L1_001 (stair): type stair is parametric in the catalogue

## Library assets and licences

- abo_B07BWJCBY2 (abo, CC-BY-4.0) x 2
- gen_shower_scandinavian_9_7fb81c9a (generated, generated (TRELLIS.2-4B, MIT)) x 1
- gen_sink_kitchen_industrial_4_3f68e743 (generated, generated (TRELLIS.2-4B, MIT)) x 2
- gen_toilet_minimal_1_3799392b (generated, generated (TRELLIS.2-4B, MIT)) x 1
- objaverse_08f7f65edfea417b8ed9ca748381e507 (objaverse, CC-BY-4.0) x 1
- objaverse_68d69bbf7a454a09a2536ac0762532f3 (objaverse, CC-BY-4.0) x 2
- objaverse_934716ccd00d4f6ba9555d1cea788488 (objaverse, CC-BY-4.0) x 2
- objaverse_f76c502218884914a27148f656a9b656 (objaverse, CC-BY-4.0) x 1

## Ranking (fit v2)

Rule: style -> bed rule -> generated last -> real size (known units first, mean |scale - 1| in 5 % steps) -> quality (missing = 3) -> aspect error -> source (abo, polyhaven, objaverse, generated).

- f_L-1_002 (fridge): objaverse_68d69bbf7a454a09a2536ac0762532f3 (objaverse), rank 1 of 1 tried: units not known (normalised by type): ranked after the real-size models; quality 3; aspect error 0.038; source objaverse
- f_L-1_003 (stove): objaverse_934716ccd00d4f6ba9555d1cea788488 (objaverse), rank 2 of 2 tried: units not known (normalised by type): ranked after the real-size models; quality 3; aspect error 0.071; source objaverse; passed over electric_stove (caps)
- f_L-1_005 (sofa): abo_B07BWJCBY2 (abo), rank 1 of 1 tried: real size: mean |scale - 1| 0.045 (step 0); quality 3; aspect error 0.119; source abo
- f_L-1_006 (sink_kitchen): gen_sink_kitchen_industrial_4_3f68e743 (generated), rank 1 of 1 tried: generated: no other library model passed the caps; units not known (normalised by type): ranked after the real-size models; quality 3; aspect error 0.049; source generated
- f_L-1b_002 (fridge): objaverse_68d69bbf7a454a09a2536ac0762532f3 (objaverse), rank 1 of 1 tried: units not known (normalised by type): ranked after the real-size models; quality 3; aspect error 0.038; source objaverse
- f_L-1b_003 (stove): objaverse_934716ccd00d4f6ba9555d1cea788488 (objaverse), rank 2 of 2 tried: units not known (normalised by type): ranked after the real-size models; quality 3; aspect error 0.071; source objaverse; passed over electric_stove (caps)
- f_L-1b_005 (sofa): abo_B07BWJCBY2 (abo), rank 1 of 1 tried: real size: mean |scale - 1| 0.045 (step 0); quality 3; aspect error 0.119; source abo
- f_L-1b_006 (sink_kitchen): gen_sink_kitchen_industrial_4_3f68e743 (generated), rank 1 of 1 tried: generated: no other library model passed the caps; units not known (normalised by type): ranked after the real-size models; quality 3; aspect error 0.049; source generated
- f_L0_002 (bed_double): objaverse_08f7f65edfea417b8ed9ca748381e507 (objaverse), rank 20 of 20 tried: units not known (normalised by type): ranked after the real-size models; quality 3; aspect error 0.089; source objaverse; passed over abo_B08FTN8KHY, abo_B0154VUESC, abo_B07GFDZW5W, abo_B075QDMWTP, abo_B071W2SCTJ, abo_B084ZBDPG5, abo_B071FJR4FW, abo_B07L1DDXLR, abo_B086TGFT35, abo_B084ZBX1YH, abo_B01N6AQX0A, abo_B075Z8767S, abo_B072PWGSZL, abo_B07B4YNHSN, abo_B07B4Z9Q3S, abo_B01M0ZVGCQ, abo_B07GFFR415, GothicBed_01, abo_B07BBWMPJM (caps)
- f_L0_003 (shower): gen_shower_scandinavian_9_7fb81c9a (generated), rank 1 of 1 tried: generated: no other library model passed the caps; units not known (normalised by type): ranked after the real-size models; quality 3; aspect error 0.074; source generated
- f_L0_004 (toilet): gen_toilet_minimal_1_3799392b (generated), rank 9 of 9 tried: generated: no other library model passed the caps; units not known (normalised by type): ranked after the real-size models; quality 3; aspect error 0.058; source generated; passed over objaverse_0b3325fad3e740b1ac86173c90b56afd, objaverse_24d1b493899d407780140688abae19bc, objaverse_3446229dce1f47528fa871cc7669136c, objaverse_5b18711616054a44b025d9272b745a6a, objaverse_bd0f8d2bfba24376bec2b827a0cbbabe, objaverse_4398bcb5976945b08f195816340247b8, objaverse_c901dfa120a0487a9f5c9a2d241f70ab, objaverse_1bd73c9a74d14ce29e45c277570990e6 (caps)
- f_L0_005 (washbasin): objaverse_f76c502218884914a27148f656a9b656 (objaverse), rank 1 of 1 tried: units not known (normalised by type): ranked after the real-size models; quality 3; aspect error 0.006; source objaverse

## Attribution (CC BY 4.0)

- abo_B07BWJCBY2: "Amazon Brand – Stone & Beam Bradbury Chesterfield Tufted Leather Loveseat Sofa Couch, 78.7"W, Black" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- objaverse_08f7f65edfea417b8ed9ca748381e507: "Bed" by Ambriel (https://sketchfab.com/3d-models/08f7f65edfea417b8ed9ca748381e507), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- objaverse_68d69bbf7a454a09a2536ac0762532f3: "Old Fridge" by golddog (https://sketchfab.com/3d-models/68d69bbf7a454a09a2536ac0762532f3), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- objaverse_934716ccd00d4f6ba9555d1cea788488: "R RETRO FIRIN" by Motto Teknoloji (https://sketchfab.com/3d-models/934716ccd00d4f6ba9555d1cea788488), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- objaverse_f76c502218884914a27148f656a9b656: "Bathroom1" by neutralize (https://sketchfab.com/3d-models/f76c502218884914a27148f656a9b656), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
