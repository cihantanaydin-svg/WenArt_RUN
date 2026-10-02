# Furniture fit report: building_fitted

Project: synthetic-03; 21 pieces, 9 library fits, 12 parametric fallbacks. Non-uniform scale cap 15 %. Footprints, types, rotations, rooms and statuses are as in the building JSON (fitting never changes them).

| piece | room | type | source | status | footprint w x d (m) | method | asset | licence | scale x / y / z | aspect err | height (m) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| f_L0_001 | r_L0_salon | sofa | from_documents | verified | 2.20 x 0.90 | library | sofa_02 | CC0 | 1.217 / 1.101 / 1.159 | 0.101 | 0.82 |
| f_L0_002 | r_L0_salon | armchair | from_documents | verified | 0.90 x 0.90 | library | ArmChair_01 | CC0 | 1.061 / 1.175 / 1.118 | 0.102 | 1.19 |
| f_L0_003 | r_L0_salon | armchair | from_documents | verified | 0.90 x 0.90 | library | ArmChair_01 | CC0 | 1.061 / 1.175 / 1.118 | 0.102 | 1.19 |
| f_L0_004 | r_L0_salon | table_coffee | from_documents | verified | 1.00 x 0.60 | parametric | parametric:table_coffee | n/a | 1.000 / 1.000 / 1.000 | - | 0.45 |
| f_L0_005 | r_L0_salon | tv_unit | from_documents | verified | 1.60 x 0.45 | parametric | parametric:tv_unit | n/a | 1.000 / 1.000 / 1.000 | - | 0.50 |
| f_L0_006 | r_L0_salon | bookshelf | from_documents | verified | 1.00 x 0.35 | library | wooden_display_shelves_01 | CC0 | 0.928 / 0.942 / 0.935 | 0.015 | 1.46 |
| f_L0_007 | r_L0_mutfak | kitchen_counter | from_documents | verified | 2.40 x 0.60 | parametric | parametric:kitchen_counter | n/a | 1.000 / 1.000 / 1.000 | - | 0.90 |
| f_L0_008 | r_L0_mutfak | sink_kitchen | from_documents | verified | 0.80 x 0.50 | parametric | parametric:sink_kitchen | n/a | 1.000 / 1.000 / 1.000 | - | 1.15 |
| f_L0_009 | r_L0_mutfak | stove | from_documents | verified | 0.60 x 0.60 | parametric | parametric:stove | n/a | 1.000 / 1.000 / 1.000 | - | 0.91 |
| f_L0_010 | r_L0_mutfak | fridge | from_documents | verified | 0.70 x 0.70 | parametric | parametric:fridge | n/a | 1.000 / 1.000 / 1.000 | - | 1.80 |
| f_L0_011 | r_L0_mutfak | table_dining | from_documents | verified | 1.60 x 0.90 | parametric | parametric:table_dining | n/a | 1.000 / 1.000 / 1.000 | - | 0.75 |
| f_L0_012 | r_L0_mutfak | chair | from_documents | verified | 0.45 x 0.45 | library | gallinera_chair | CC0 | 0.775 / 0.745 / 0.760 | 0.039 | 0.79 |
| f_L0_013 | r_L0_mutfak | chair | from_documents | verified | 0.45 x 0.45 | library | gallinera_chair | CC0 | 0.775 / 0.745 / 0.760 | 0.039 | 0.79 |
| f_L0_014 | r_L0_yatak_odasi | bed_double | from_documents | verified | 1.60 x 2.00 | library | GothicBed_01 | CC0 | 1.071 / 0.980 / 1.026 | 0.088 | 1.57 |
| f_L0_015 | r_L0_yatak_odasi | nightstand | from_documents | verified | 0.50 x 0.40 | library | side_table_01 | CC0 | 0.909 / 0.889 / 0.899 | 0.022 | 0.50 |
| f_L0_016 | r_L0_yatak_odasi | nightstand | from_documents | verified | 0.50 x 0.40 | library | side_table_01 | CC0 | 0.909 / 0.889 / 0.899 | 0.022 | 0.50 |
| f_L0_017 | r_L0_yatak_odasi | wardrobe | from_documents | verified | 1.80 x 0.60 | parametric | parametric:wardrobe | n/a | 1.000 / 1.000 / 1.000 | - | 2.10 |
| f_L0_018 | r_L0_yatak_odasi | dresser | from_documents | verified | 1.20 x 0.50 | parametric | parametric:dresser | n/a | 1.000 / 1.000 / 1.000 | - | 0.80 |
| f_L0_019 | r_L0_wc | toilet | from_documents | verified | 0.40 x 0.70 | parametric | parametric:toilet | n/a | 1.000 / 1.000 / 1.000 | - | 0.80 |
| f_L0_020 | r_L0_wc | washbasin | from_documents | verified | 0.60 x 0.45 | parametric | parametric:washbasin | n/a | 1.000 / 1.000 / 1.000 | - | 1.00 |
| f_L0_021 | r_L0_kiler | unknown | from_documents | unverified | 1.20 x 0.50 | parametric | parametric:unknown | n/a | 1.000 / 1.000 / 1.000 | - | 0.80 |

## Parametric fallbacks

- f_L0_004 (table_coffee): no table_coffee candidate within 15 % non-uniform scale and 0.75..1.3 mean scale (closest: CoffeeTable_01 at 5.3 % non-uniform, mean scale 0.6331)
- f_L0_005 (tv_unit): no tv_unit candidate within 15 % non-uniform scale and 0.75..1.3 mean scale (closest: modern_wooden_cabinet at 32.0 % non-uniform, mean scale 0.7606)
- f_L0_007 (kitchen_counter): type kitchen_counter is parametric in the catalogue
- f_L0_008 (sink_kitchen): type sink_kitchen is parametric in the catalogue
- f_L0_009 (stove): no stove candidate within 15 % non-uniform scale and 0.75..1.3 mean scale (closest: electric_stove at 28.8 % non-uniform, mean scale 1.0601)
- f_L0_010 (fridge): type fridge is parametric in the catalogue
- f_L0_011 (table_dining): no table_dining candidate within 15 % non-uniform scale and 0.75..1.3 mean scale (closest: dining_table at 9.6 % non-uniform, mean scale 0.6783)
- f_L0_017 (wardrobe): type wardrobe is parametric in the catalogue
- f_L0_018 (dresser): no dresser candidate within 15 % non-uniform scale and 0.75..1.3 mean scale (closest: GothicCommode_01 at 16.0 % non-uniform, mean scale 0.9299)
- f_L0_019 (toilet): type toilet is parametric in the catalogue
- f_L0_020 (washbasin): type washbasin is parametric in the catalogue
- f_L0_021 (unknown): type unknown is parametric in the catalogue

## Library assets and licences

- ArmChair_01 (polyhaven, CC0) x 2
- GothicBed_01 (polyhaven, CC0) x 1
- gallinera_chair (polyhaven, CC0) x 2
- side_table_01 (polyhaven, CC0) x 2
- sofa_02 (polyhaven, CC0) x 1
- wooden_display_shelves_01 (polyhaven, CC0) x 1
