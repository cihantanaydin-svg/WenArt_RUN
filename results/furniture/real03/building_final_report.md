# Furniture fit report: building_final

Project: real03; 12 pieces, 9 library fits, 3 parametric fallbacks. Non-uniform scale cap 15 %. Footprints, types, rotations, rooms and statuses are as in the building JSON (fitting never changes them).

Library style filter: family 'modern' (the profile's family, outputs/real03/style.json): library models only when their styles hold 'modern' or 'neutral'

| piece | room | type | source | status | footprint w x d (m) | method | asset | licence | scale x / y / z | aspect err | height (m) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| f_L0_001 | r_L0_yangin_merdiveni | kitchen_counter | from_documents | unverified | 2.60 x 0.55 | parametric | parametric:kitchen_counter | n/a | 1.000 / 1.000 / 1.000 | - | 0.90 |
| f_L0_002 | r_L0_kat_merdiveni | kitchen_island | from_documents | unverified | 2.60 x 0.55 | parametric | parametric:kitchen_island | n/a | 1.000 / 1.000 / 1.000 | - | 0.90 |
| f_L0_003 | r_L0_kat_holu | unknown | from_documents | unverified | 0.90 x 0.34 | parametric | parametric:unknown | n/a | 1.000 / 1.000 / 1.000 | - | 0.80 |
| f_L0_004 | r_L0_ruzgarlik | desk | added_by_ai | verified | 1.40 x 0.70 | library | abo_B07B7DKRW4 | CC-BY-4.0 | 1.087 / 1.111 / 1.099 | 0.023 | 0.95 |
| f_L0_005 | r_L0_ruzgarlik | bookshelf | added_by_ai | verified | 1.00 x 0.35 | library | objaverse_d48a42e91c5d4716a8c254addf8c9d99 | CC-BY-4.0 | 0.851 / 0.904 / 0.877 | 0.061 | 1.66 |
| f_L0_006 | r_L0_guvenlik_holu | console_table | added_by_ai | verified | 1.20 x 0.35 | library | abo_B01DA8QZFM | CC-BY-4.0 | 0.968 / 1.001 / 0.984 | 0.033 | 0.72 |
| f_L0_007 | r_L0_guvenlik_holu | shoe_cabinet | added_by_ai | verified | 0.80 x 0.32 | library | gen_shoe_cabinet_scandinavian_2_66dac02b | generated (TRELLIS.2-4B, MIT) | 0.800 / 0.722 / 0.761 | 0.103 | 0.76 |
| f_L0_008 | r_L0_guvenlik_holu | bench | added_by_ai | verified | 1.20 x 0.40 | library | abo_B07K7NQR23 | CC-BY-4.0 | 1.000 / 0.988 / 0.994 | 0.012 | 0.48 |
| f_L0_009 | r_L0_guvenlik_holu | bookshelf | added_by_ai | verified | 1.00 x 0.35 | library | objaverse_d48a42e91c5d4716a8c254addf8c9d99 | CC-BY-4.0 | 0.851 / 0.904 / 0.877 | 0.061 | 1.66 |
| f_L0_010 | r_L0_kat_holu | console_table | added_by_ai | verified | 1.20 x 0.35 | library | abo_B01DA8QZFM | CC-BY-4.0 | 0.968 / 1.001 / 0.984 | 0.033 | 0.72 |
| f_L0_012 | r_L0_yangin_merdiveni | chair | added_by_ai | verified | 0.50 x 0.50 | library | objaverse_d2785b57e7da45858f2fe8bf4dedd68d | CC-BY-4.0 | 0.968 / 0.994 / 0.981 | 0.027 | 0.81 |
| f_L0_013 | r_L0_yangin_merdiveni | table_dining | added_by_ai | verified | 1.20 x 0.80 | library | abo_B07SJ75Y1M | CC-BY-4.0 | 0.923 / 0.889 / 0.906 | 0.038 | 0.68 |

## Parametric fallbacks

- f_L0_001 (kitchen_counter): type kitchen_counter is parametric in the catalogue
- f_L0_002 (kitchen_island): type kitchen_island is parametric in the catalogue
- f_L0_003 (unknown): type unknown is parametric in the catalogue

## Library assets and licences

- abo_B01DA8QZFM (abo, CC-BY-4.0) x 2
- abo_B07B7DKRW4 (abo, CC-BY-4.0) x 1
- abo_B07K7NQR23 (abo, CC-BY-4.0) x 1
- abo_B07SJ75Y1M (abo, CC-BY-4.0) x 1
- gen_shoe_cabinet_scandinavian_2_66dac02b (generated, generated (TRELLIS.2-4B, MIT)) x 1
- objaverse_d2785b57e7da45858f2fe8bf4dedd68d (objaverse, CC-BY-4.0) x 1
- objaverse_d48a42e91c5d4716a8c254addf8c9d99 (objaverse, CC-BY-4.0) x 2

## Ranking (fit v2)

Rule: style -> bed rule -> generated last -> real size (known units first, mean |scale - 1| in 5 % steps) -> quality (missing = 3) -> aspect error -> source (abo, polyhaven, objaverse, generated).

- f_L0_004 (desk): abo_B07B7DKRW4 (abo), rank 1 of 1 tried: real size: mean |scale - 1| 0.099 (step 1); quality 3; aspect error 0.023; source abo
- f_L0_005 (bookshelf): objaverse_d48a42e91c5d4716a8c254addf8c9d99 (objaverse), rank 10 of 10 tried: units not known (normalised by type): ranked after the real-size models; quality 3; aspect error 0.061; source objaverse; passed over abo_B07H8SQ2NZ, abo_B07JGY5LNV, abo_B082JGV1YM, abo_B07H8P1N9T, abo_B07B7J2VCD, abo_B07HSCNKCT, abo_B07PQS58XN, abo_B07PSZHDNK, abo_B07PMK78R8 (caps)
- f_L0_006 (console_table): abo_B01DA8QZFM (abo), rank 1 of 1 tried: real size: mean |scale - 1| 0.016 (step 0); quality 3; aspect error 0.033; source abo
- f_L0_007 (shoe_cabinet): gen_shoe_cabinet_scandinavian_2_66dac02b (generated), rank 6 of 6 tried: generated: no other library model passed the caps; units not known (normalised by type): ranked after the real-size models; quality 3; aspect error 0.103; source generated; passed over abo_B07K7YMBNY, abo_B07GFS1R7X, abo_B07TVMZ5QP, abo_B07TVN114C, abo_B07GFDZVYY (caps)
- f_L0_008 (bench): abo_B07K7NQR23 (abo), rank 3 of 3 tried: real size: mean |scale - 1| 0.006 (step 0); quality 3; aspect error 0.012; source abo; passed over abo_B07HSBDCX8, objaverse_22e8163cf6e1413486faeb4e42222a99 (caps)
- f_L0_009 (bookshelf): objaverse_d48a42e91c5d4716a8c254addf8c9d99 (objaverse), rank 10 of 10 tried: units not known (normalised by type): ranked after the real-size models; quality 3; aspect error 0.061; source objaverse; passed over abo_B07H8SQ2NZ, abo_B07JGY5LNV, abo_B082JGV1YM, abo_B07H8P1N9T, abo_B07B7J2VCD, abo_B07HSCNKCT, abo_B07PQS58XN, abo_B07PSZHDNK, abo_B07PMK78R8 (caps)
- f_L0_010 (console_table): abo_B01DA8QZFM (abo), rank 1 of 1 tried: real size: mean |scale - 1| 0.016 (step 0); quality 3; aspect error 0.033; source abo
- f_L0_012 (chair): objaverse_d2785b57e7da45858f2fe8bf4dedd68d (objaverse), rank 1 of 1 tried: units not known (normalised by type): ranked after the real-size models; quality 3; aspect error 0.027; source objaverse
- f_L0_013 (table_dining): abo_B07SJ75Y1M (abo), rank 1 of 1 tried: real size: mean |scale - 1| 0.094 (step 1); quality 3; aspect error 0.038; source abo

## Recolour and colour matches (Milestone 10)

- f_L0_004: abo_B07B7DKRW4 wood slots [0] recoloured wood_veneer_oak_light
- f_L0_005: objaverse_d48a42e91c5d4716a8c254addf8c9d99 wood slots [0] recoloured wood_veneer_oak_light
- f_L0_006: abo_B01DA8QZFM wood slots [0] recoloured wood_veneer_oak_light
- f_L0_009: objaverse_d48a42e91c5d4716a8c254addf8c9d99 wood slots [0] recoloured wood_veneer_oak_light
- f_L0_010: abo_B01DA8QZFM wood slots [0] recoloured wood_veneer_oak_light
- f_L0_012: objaverse_d2785b57e7da45858f2fe8bf4dedd68d wood slots [0] recoloured wood_veneer_oak_light
- f_L0_013: abo_B07SJ75Y1M wood slots [0] recoloured wood_veneer_oak_light

## Models not taken (mattress rule, style filter, design)

- f_L0_004: metal_office_desk: styles ['industrial'] include neither modern nor neutral
- f_L0_004: WoodenTable_01: styles ['rustic'] include neither modern nor neutral
- f_L0_004: SchoolDesk_01: styles ['industrial'] include neither modern nor neutral
- f_L0_004: abo_B01MXKMRK4: styles ['modern minimal', 'industrial'] include neither modern nor neutral
- f_L0_004: abo_B07B7DFS3S: styles ['industrial', 'rustic'] include neither modern nor neutral
- f_L0_004: abo_B07PVL2N3D: styles ['modern minimal', 'industrial'] include neither modern nor neutral
- f_L0_004: abo_B07PYYRV2L: styles ['modern minimal', 'industrial'] include neither modern nor neutral
- f_L0_004: abo_B07QV37J6B: styles ['modern minimal', 'industrial'] include neither modern nor neutral
- f_L0_004: abo_B07RVBPWG9: styles ['modern minimal', 'industrial'] include neither modern nor neutral
- f_L0_004: abo_B082DFL4JW: styles ['japandi', 'modern minimal', 'industrial'] include neither modern nor neutral
- f_L0_005: Shelf_01: styles ['rustic'] include neither modern nor neutral
- f_L0_005: wooden_bookshelf_worn: styles ['rustic'] include neither modern nor neutral
- f_L0_005: abo_B074KKXLK1: styles ['modern minimal', 'minimal'] include neither modern nor neutral
- f_L0_005: abo_B075Z6YS1Z: styles ['industrial'] include neither modern nor neutral
- f_L0_005: abo_B07HSCJZQM: styles ['modern minimal', 'industrial'] include neither modern nor neutral
- f_L0_005: abo_B07QC876WJ: styles ['scandinavian', 'modern minimal', 'industrial'] include neither modern nor neutral
- f_L0_005: objaverse_4939d1bca386405f9cc22c48441b63de: styles ['modern minimal', 'industrial'] include neither modern nor neutral
- f_L0_005: objaverse_68baafb344b2445a8e7f4917b6fe8a63: styles ['classic'] include neither modern nor neutral
- f_L0_005: objaverse_6c5ac2547db34c3c81b2e4808b000386: styles ['classic'] include neither modern nor neutral
- f_L0_005: objaverse_7a545709aa98429a9b30f812f70193f7: styles ['modern minimal', 'minimal'] include neither modern nor neutral
- f_L0_006: abo_B075Z99L7R: styles ['modern minimal', 'industrial'] include neither modern nor neutral
- f_L0_006: abo_B075ZCLPS1: styles ['industrial'] include neither modern nor neutral
- f_L0_006: abo_B07DB9638P: styles ['classic'] include neither modern nor neutral
- f_L0_006: abo_B07HSBHY2P: styles ['classic'] include neither modern nor neutral
- f_L0_006: abo_B07W563NHG: styles ['modern minimal', 'minimal', 'industrial'] include neither modern nor neutral
- f_L0_006: gen_console_table_classic_1_3039559c: styles ['classic'] include neither modern nor neutral
- f_L0_006: gen_console_table_classic_2_781fd7f9: styles ['classic'] include neither modern nor neutral
- f_L0_006: gen_console_table_industrial_2_b39850f8: styles ['industrial'] include neither modern nor neutral
- f_L0_007: abo_B07GFDZWMS: styles ['modern minimal', 'minimal'] include neither modern nor neutral
- f_L0_007: abo_B07GFF11HV: styles ['modern minimal', 'minimal'] include neither modern nor neutral
- f_L0_007: abo_B07GFLG5MM: styles ['modern minimal', 'minimal'] include neither modern nor neutral
- f_L0_007: abo_B07GFS1WH7: styles ['rustic'] include neither modern nor neutral
- f_L0_007: abo_B07P64ZJQG: styles ['modern minimal', 'minimal'] include neither modern nor neutral
- f_L0_007: abo_B07P652THV: styles ['modern minimal', 'minimal'] include neither modern nor neutral
- f_L0_007: abo_B07TWQTVXL: styles ['modern minimal'] include neither modern nor neutral
- f_L0_007: gen_shoe_cabinet_classic_3_d5d17132: styles ['classic'] include neither modern nor neutral
- f_L0_007: gen_shoe_cabinet_industrial_1_23a27737: styles ['modern minimal', 'industrial'] include neither modern nor neutral
- f_L0_007: gen_shoe_cabinet_industrial_3_596e817a: styles ['industrial'] include neither modern nor neutral
- f_L0_007: gen_shoe_cabinet_mediterranean_1_5b538be0: styles ['scandinavian', 'modern minimal', 'minimal'] include neither modern nor neutral
- f_L0_008: abo_B07DBCFM4F: styles ['classic'] include neither modern nor neutral
- f_L0_008: abo_B0871DCNRM: styles ['modern minimal', 'minimal'] include neither modern nor neutral
- f_L0_008: objaverse_43dfa2813779487b9d1bb36b7c1a321c: styles ['rustic'] include neither modern nor neutral
- f_L0_008: objaverse_83bb7dff14e84ecbbc99ebb80fe2977c: styles ['japandi', 'modern minimal', 'minimal', 'industrial'] include neither modern nor neutral
- f_L0_008: objaverse_9a4d1c954ed446d9a8d436d5be6dedca: styles ['classic'] include neither modern nor neutral
- f_L0_008: objaverse_da39bc3a29364f8bb4bf45bccf856bdc: styles ['japandi', 'rustic'] include neither modern nor neutral
- f_L0_009: Shelf_01: styles ['rustic'] include neither modern nor neutral
- f_L0_009: wooden_bookshelf_worn: styles ['rustic'] include neither modern nor neutral
- f_L0_009: abo_B074KKXLK1: styles ['modern minimal', 'minimal'] include neither modern nor neutral
- f_L0_009: abo_B075Z6YS1Z: styles ['industrial'] include neither modern nor neutral
- f_L0_009: abo_B07HSCJZQM: styles ['modern minimal', 'industrial'] include neither modern nor neutral
- f_L0_009: abo_B07QC876WJ: styles ['scandinavian', 'modern minimal', 'industrial'] include neither modern nor neutral
- f_L0_009: objaverse_4939d1bca386405f9cc22c48441b63de: styles ['modern minimal', 'industrial'] include neither modern nor neutral
- f_L0_009: objaverse_68baafb344b2445a8e7f4917b6fe8a63: styles ['classic'] include neither modern nor neutral
- f_L0_009: objaverse_6c5ac2547db34c3c81b2e4808b000386: styles ['classic'] include neither modern nor neutral
- f_L0_009: objaverse_7a545709aa98429a9b30f812f70193f7: styles ['modern minimal', 'minimal'] include neither modern nor neutral
- f_L0_010: abo_B075Z99L7R: styles ['modern minimal', 'industrial'] include neither modern nor neutral
- f_L0_010: abo_B075ZCLPS1: styles ['industrial'] include neither modern nor neutral
- f_L0_010: abo_B07DB9638P: styles ['classic'] include neither modern nor neutral
- f_L0_010: abo_B07HSBHY2P: styles ['classic'] include neither modern nor neutral
- f_L0_010: abo_B07W563NHG: styles ['modern minimal', 'minimal', 'industrial'] include neither modern nor neutral
- f_L0_010: gen_console_table_classic_1_3039559c: styles ['classic'] include neither modern nor neutral
- f_L0_010: gen_console_table_classic_2_781fd7f9: styles ['classic'] include neither modern nor neutral
- f_L0_010: gen_console_table_industrial_2_b39850f8: styles ['industrial'] include neither modern nor neutral
- f_L0_012: gallinera_chair: styles ['classic', 'rustic'] include neither modern nor neutral
- f_L0_012: painted_wooden_chair_02: styles ['rustic'] include neither modern nor neutral
- f_L0_012: abo_B07DBD9WHX: styles ['classic'] include neither modern nor neutral
- f_L0_012: abo_B07DBHCKHY: styles ['classic'] include neither modern nor neutral
- f_L0_012: abo_B07FY8PZBH: styles ['industrial'] include neither modern nor neutral
- f_L0_012: abo_B07QJ24FSL: styles ['classic'] include neither modern nor neutral
- f_L0_012: abo_B0857JLP6K: styles ['minimal', 'industrial'] include neither modern nor neutral
- f_L0_012: objaverse_0723b35415b0462eb5c01140b6b70340: styles ['classic'] include neither modern nor neutral
- f_L0_012: objaverse_1625701880c54b7d9f50e77455cef39b: styles ['mediterranean'] include neither modern nor neutral
- f_L0_012: objaverse_47a690dcecf847fca99c4f89111db85b: styles ['classic', 'rustic'] include neither modern nor neutral
- f_L0_012: objaverse_cb43e2abac66494d81e1e7116eb47043: styles ['industrial', 'rustic'] include neither modern nor neutral
- f_L0_013: dining_table: styles ['rustic'] include neither modern nor neutral
- f_L0_013: wooden_table_02: styles ['rustic'] include neither modern nor neutral
- f_L0_013: painted_wooden_table: styles ['rustic'] include neither modern nor neutral
- f_L0_013: abo_B075Z9QB7N: styles ['industrial'] include neither modern nor neutral
- f_L0_013: abo_B07B7BGXN9: styles ['rustic'] include neither modern nor neutral
- f_L0_013: abo_B07H93GTHW: styles ['modern minimal', 'industrial'] include neither modern nor neutral
- f_L0_013: abo_B07RT5JN33: styles ['modern minimal', 'industrial'] include neither modern nor neutral
- f_L0_013: objaverse_724d93a7f3644f96909e8c55909c6418: styles ['scandinavian', 'rustic'] include neither modern nor neutral

## Attribution (CC BY 4.0)

- abo_B01DA8QZFM: "Amazon Brand - Movian Corona Console Table, 2 Drawer With Shelf, Solid Pine Wood, 70 x 83 x 31 cm" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- abo_B07B7DKRW4: "Amazon Brand – Stone & Beam Anne Farmhouse French Wood Desk, 62"W, Blue" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- abo_B07HKCRWJH: "Amazon Brand – Rivet Mid-Century Modern Ceiling Hanging Pendant Fixture with Light Bulb - 14.25 x 14.25 x 11.25 Inches, 12-120 Inch Cord, Satin Brass" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- abo_B07HKGHSR7: "Amazon Brand – Rivet Modern Two Tone Table Desk Lamp with LED Light Bulb and Drum Shade - 12 x 12 x 15.88 Inches, Matte Black and Antique Brass" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- abo_B07K7NQR23: "Marca Amazon - Alkove - Hayes - Banco de madera maciza con asiento tapizado (roble salvaje)" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- abo_B07QD6ZV84: "Amazon Brand – Stone & Beam Mid-Century Rustic Vase, 8.66"H, Neutral" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- abo_B07SJ75Y1M: "Amazon Brand - Alkove Hayes Classic Fixed Solid Wood Dining Table, Seats 4-6, 130 x 90 x 75cm, Wild Oak" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- abo_B084HV5LK3: "Amazon Brand - Rivet Modern Oval Hanging Mirror, 39"H, Gold" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- objaverse_d2785b57e7da45858f2fe8bf4dedd68d: "Chair" by 杭州维界科技有限公司 (https://sketchfab.com/3d-models/d2785b57e7da45858f2fe8bf4dedd68d), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- objaverse_d48a42e91c5d4716a8c254addf8c9d99: "High Bookcase" by 8549 (https://sketchfab.com/3d-models/d48a42e91c5d4716a8c254addf8c9d99), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched

## Decor

- mirror: abo_B084HV5LK3 x 1
- pendant_light: abo_B07HKCRWJH x 1
- plant: gen_potted_plant_japandi_3_36d34f2a x 1
- plant_large: gen_plant_large_japandi_5_92708e0b x 2
- plant_large: gen_plant_large_mediterranean_4_b7e80c9d x 1
- plant_large: gen_plant_large_minimal_4_71886746 x 1
- plant_large: gen_plant_large_scandinavian_1_2265e7c5 x 1
- plant_small: gen_plant_small_classic_4_53050a52 x 1
- plant_small: gen_plant_small_scandinavian_1_0dcfdd60 x 1
- table_lamp: abo_B07HKGHSR7 x 1
- vase: abo_B07QD6ZV84 x 1
- books are parametric by design; cushions, plants and rugs without a library decor model of the style family (or neutral) are parametric, wall art without one is not built

## Locked check (docs/milestone10.md §2.7)

source outputs/real03/building.json, mode complete (from outputs/real03/completion.json)

- pass
