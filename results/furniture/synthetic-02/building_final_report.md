# Furniture fit report: building_final

Project: synthetic-02; 16 pieces, 0 library fits, 16 parametric fallbacks. Non-uniform scale cap 15 %. Footprints, types, rotations, rooms and statuses are as in the building JSON (fitting never changes them).

Library style filter: family 'scandinavian' (the profile's family, outputs/synthetic-02/style.json): library models only when their styles hold 'scandinavian' or 'neutral'

| piece | room | type | source | status | footprint w x d (m) | method | asset | licence | scale x / y / z | aspect err | height (m) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| f_L0_001 | r_L0_yatak_odasi | unknown | from_documents | unverified | 2.09 x 2.05 | parametric | parametric:unknown | n/a | 1.000 / 1.000 / 1.000 | - | 0.80 |
| f_L0_002 | r_L0_salon | unknown | from_documents | unverified | 0.53 x 3.19 | parametric | parametric:unknown | n/a | 1.000 / 1.000 / 1.000 | - | 0.80 |
| f_L0_003 | r_L0_mutfak | kitchen_counter | from_documents | verified | 2.46 x 0.66 | parametric | parametric:kitchen_counter | n/a | 1.000 / 1.000 / 1.000 | - | 0.90 |
| f_L0_004 | r_L0_mutfak | unknown | from_documents | unverified | 1.64 x 0.95 | parametric | parametric:unknown | n/a | 1.000 / 1.000 / 1.000 | - | 0.80 |
| f_L0_005 | r_L0_salon | unknown | from_documents | unverified | 1.62 x 0.93 | parametric | parametric:unknown | n/a | 1.000 / 1.000 / 1.000 | - | 0.80 |
| f_L0_006 | r_L0_yatak_odasi | wardrobe | from_documents | verified | 1.81 x 0.69 | parametric | parametric:wardrobe | n/a | 1.000 / 1.000 / 1.000 | - | 2.10 |
| f_L0_007 | r_L0_yatak_odasi | unknown | from_documents | unverified | 1.42 x 0.76 | parametric | parametric:unknown | n/a | 1.000 / 1.000 / 1.000 | - | 0.80 |
| f_L0_008 | r_L0_banyo | shower | from_documents | verified | 1.00 x 0.93 | parametric | parametric:shower | n/a | 1.000 / 1.000 / 1.000 | - | 2.00 |
| f_L0_009 | r_L0_salon | fridge | from_documents | unverified | 0.92 x 0.92 | parametric | parametric:fridge | n/a | 1.000 / 1.000 / 1.000 | - | 1.80 |
| f_L0_010 | r_L0_banyo | shower | from_documents | verified | 0.79 x 0.83 | parametric | parametric:shower | n/a | 1.000 / 1.000 / 1.000 | - | 2.00 |
| f_L0_011 | r_L0_salon | table_coffee | from_documents | verified | 1.03 x 0.63 | parametric | parametric:table_coffee | n/a | 1.000 / 1.000 / 1.000 | - | 0.45 |
| f_L0_012 | r_L0_mutfak | unknown | from_documents | unverified | 0.70 x 0.73 | parametric | parametric:unknown | n/a | 1.000 / 1.000 / 1.000 | - | 0.80 |
| f_L0_013 | r_L0_banyo | unknown | from_documents | unverified | 0.72 x 0.68 | parametric | parametric:unknown | n/a | 1.000 / 1.000 / 1.000 | - | 0.80 |
| f_L0_014 | r_L0_antre | unknown | from_documents | unverified | 1.02 x 0.42 | parametric | parametric:unknown | n/a | 1.000 / 1.000 / 1.000 | - | 0.80 |
| f_L0_015 | r_L0_banyo | unknown | from_documents | unverified | 0.79 x 0.43 | parametric | parametric:unknown | n/a | 1.000 / 1.000 / 1.000 | - | 0.80 |
| f_L0_016 | r_L0_banyo | washbasin | from_documents | verified | 0.39 x 0.76 | parametric | parametric:washbasin | n/a | 1.000 / 1.000 / 1.000 | - | 1.00 |

## Parametric fallbacks

- f_L0_001 (unknown): type unknown is parametric in the catalogue
- f_L0_002 (unknown): type unknown is parametric in the catalogue
- f_L0_003 (kitchen_counter): type kitchen_counter is parametric in the catalogue
- f_L0_004 (unknown): type unknown is parametric in the catalogue
- f_L0_005 (unknown): type unknown is parametric in the catalogue
- f_L0_006 (wardrobe): no wardrobe candidate within 15 % non-uniform scale and 0.75..1.3 mean scale (closest: objaverse_b46803ba0bc64e12b31f832fb761c4e0 at 40.3 % non-uniform, mean scale 1.4837)
- f_L0_007 (unknown): type unknown is parametric in the catalogue
- f_L0_008 (shower): type shower is parametric in the catalogue
- f_L0_009 (fridge): no model for style scandinavian
- f_L0_010 (shower): type shower is parametric in the catalogue
- f_L0_011 (table_coffee): no table_coffee candidate within 15 % non-uniform scale and 0.75..1.3 mean scale (closest: objaverse_1d41e84fd76241e7a8929a314052269c at 15.8 % non-uniform, mean scale 0.9275)
- f_L0_012 (unknown): type unknown is parametric in the catalogue
- f_L0_013 (unknown): type unknown is parametric in the catalogue
- f_L0_014 (unknown): type unknown is parametric in the catalogue
- f_L0_015 (unknown): type unknown is parametric in the catalogue
- f_L0_016 (washbasin): no model for style scandinavian

## Library assets and licences

- none

## Models not taken (mattress rule and style filter)

- f_L0_006: objaverse_05a035c3347645b8a7ceb6d65f825ac3: styles ['classic'] include neither scandinavian nor neutral
- f_L0_006: objaverse_b3a99e956be64ab6958f7f5e1895f031: styles ['classic', 'rustic'] include neither scandinavian nor neutral
- f_L0_009: objaverse_2071bda681b642218b6829b82e4fd93b: styles ['modern minimal', 'minimal', 'modern'] include neither scandinavian nor neutral
- f_L0_009: objaverse_68d69bbf7a454a09a2536ac0762532f3: styles ['modern minimal', 'minimal', 'modern'] include neither scandinavian nor neutral
- f_L0_011: CoffeeTable_01: styles ['classic', 'rustic'] include neither scandinavian nor neutral
- f_L0_011: modern_coffee_table_01: styles ['modern'] include neither scandinavian nor neutral
- f_L0_011: modern_coffee_table_02: styles ['modern'] include neither scandinavian nor neutral
- f_L0_011: objaverse_b0c0c9c65d06443c87391134a62e2287: styles ['japandi', 'modern minimal', 'minimal', 'modern'] include neither scandinavian nor neutral
- f_L0_011: objaverse_c17577daa87849d09960669606c0ce27: styles ['japandi', 'modern minimal', 'minimal', 'modern'] include neither scandinavian nor neutral
- f_L0_011: objaverse_c42d069236174467a2fb536f7d42d7f0: styles ['japandi', 'modern minimal', 'minimal', 'modern'] include neither scandinavian nor neutral
- f_L0_011: objaverse_f4031bb5f7e64ebca4c37d4fa5ba6e8d: styles ['classic', 'rustic'] include neither scandinavian nor neutral
- f_L0_016: objaverse_ce1a06f7cbe1425099a145f851fc5dee: styles ['modern minimal', 'minimal', 'modern'] include neither scandinavian nor neutral
