# Library audit

## Totals

| status | models |
|---|---|
| keep | 310 |
| fix | 4 |
| removed | 38 |

## Per source

| source | keep | fix | removed | total |
|---|---|---|---|---|
| abo | 195 | 1 | 6 | 202 |
| generated | 15 | 2 | 10 | 27 |
| gso | 31 | 0 | 5 | 36 |
| polyhaven | 69 | 1 | 17 | 87 |

## Per type

| kind | type | keep | fix | removed | total |
|---|---|---|---|---|---|
| furniture | armchair | 21 | 0 | 0 | 21 |
| furniture | bar_stool | 7 | 0 | 1 | 8 |
| furniture | bench | 2 | 0 | 0 | 2 |
| furniture | bookshelf | 3 | 0 | 3 | 6 |
| furniture | chair | 13 | 0 | 3 | 16 |
| furniture | floor_lamp | 2 | 0 | 0 | 2 |
| furniture | nightstand | 5 | 0 | 0 | 5 |
| furniture | ottoman | 4 | 0 | 0 | 4 |
| furniture | side_table | 11 | 0 | 0 | 11 |
| furniture | sofa | 14 | 0 | 0 | 14 |
| furniture | sofa_corner | 8 | 1 | 0 | 9 |
| furniture | table_coffee | 11 | 0 | 0 | 11 |
| furniture | tall_cabinet | 3 | 0 | 0 | 3 |
| furniture | toilet | 0 | 2 | 1 | 3 |
| furniture | bathtub | 3 | 0 | 0 | 3 |
| furniture | washbasin | 3 | 0 | 0 | 3 |
| furniture | sink_kitchen | 0 | 0 | 3 | 3 |
| furniture | stove | 0 | 0 | 3 | 3 |
| furniture | fridge | 0 | 0 | 3 | 3 |
| decor | cushion | 40 | 0 | 0 | 40 |
| decor | rug | 40 | 0 | 0 | 40 |
| decor | wall_art | 39 | 0 | 6 | 45 |
| decor | basket | 5 | 0 | 3 | 8 |
| decor | books | 5 | 0 | 0 | 5 |
| decor | bowl | 17 | 0 | 0 | 17 |
| decor | plant_small | 16 | 0 | 2 | 18 |
| decor | tray | 0 | 0 | 1 | 1 |
| furniture | bed_single | 1 | 1 | 0 | 2 |
| furniture | console_table | 2 | 0 | 0 | 2 |
| furniture | office_chair | 1 | 0 | 0 | 1 |
| furniture | sideboard | 1 | 0 | 3 | 4 |
| furniture | table_dining | 2 | 0 | 1 | 3 |
| furniture | wardrobe | 1 | 0 | 0 | 1 |
| decor | candle | 3 | 0 | 1 | 4 |
| decor | clock | 1 | 0 | 1 | 2 |
| decor | mirror | 1 | 0 | 0 | 1 |
| decor | pendant_light | 8 | 0 | 0 | 8 |
| decor | sculpture | 7 | 0 | 3 | 10 |
| decor | table_lamp | 2 | 0 | 0 | 2 |
| decor | vase | 8 | 0 | 0 | 8 |

## Removal reasons (a model may have several)

| reason | models |
|---|---|
| vision check | 37 |
| real product off size | 15 |
| a drawer, door or lid is open, or a part floats ap | 6 |
| proportions fit no real piece | 6 |
| title flag | 5 |
| title names another type | 3 |
| lies on its side | 3 |

## Fixes (catalogue fields)

| fix | models |
|---|---|
| front_quarter_turns | 4 |

## Kept with a vision doubt (user decision 1a of 11 Oct 2026; each run's final check looks at them)

| id | type | source | status | doubt | title |
|---|---|---|---|---|---|
| abo_B07ML7PPZC | floor_lamp | abo | keep | vision quality 2 (<= 2) | Amazon Brand – Ravenna Home Floor Lamp with Shelves, LED Lig |
| infinigen_bathroom_sink_0 | washbasin | generated | keep | vision quality 2 (<= 2) | Infinigen bathroom sink (BathroomSinkFactory, seed 0) |
| infinigen_toilet_1 | toilet | generated | fix | vision quality 2 (<= 2) | Infinigen toilet (ToiletFactory, seed 1) |
| infinigen_bathtub_1 | bathtub | generated | keep | vision quality 2 (<= 2) | Infinigen bathtub (BathtubFactory, seed 1) |
| infinigen_bathroom_sink_1 | washbasin | generated | keep | the vision check sees more than one object; vision quality 1 (<= 2) | Infinigen bathroom sink (BathroomSinkFactory, seed 1) |
| infinigen_toilet_2 | toilet | generated | fix | vision quality 2 (<= 2) | Infinigen toilet (ToiletFactory, seed 2) |
| infinigen_bathtub_2 | bathtub | generated | keep | vision quality 2 (<= 2) | Infinigen bathtub (BathtubFactory, seed 2) |
| infinigen_bathroom_sink_2 | washbasin | generated | keep | vision quality 2 (<= 2) | Infinigen bathroom sink (BathroomSinkFactory, seed 2) |
| abo_B07M6PHSCP | cushion | abo | keep | vision quality 2 (<= 2) | Amazon Brand – Ravenna Home Classic Paisley Throw Pillow - 2 |
| abo_B07M6PK8QS | cushion | abo | keep | vision quality 2 (<= 2) | Amazon Brand – Ravenna Home Classic Paisley Throw Pillow, 24 |
| abo_B0732D26BZ | rug | abo | keep | vision quality 2 (<= 2) | Amazon Brand – Stone & Beam Contemporary Mode Tone Wool Area |
| abo_B073P14BDC | wall_art | abo | keep | the vision check says it is not a wall_art (a mirror) | Amazon Brand – Rivet Modern Pursuit of Happiness Word Art Fr |
| abo_B073P1LPHH | wall_art | abo | keep | the vision check sees more than one object | Amazon Brand – Stone & Beam Contemporary White Tulip Bouquet |
| abo_B075YLSBMR | wall_art | abo | keep | the vision check sees more than one object | Amazon Brand – Rivet Modern Right Facing Palm Frond Leaf Pri |
| gso_Sea_to_Summit_Xl_Bowl | bowl | gso | keep | the vision check says it is not a bowl; vision quality 2 (<= 2) | Sea to Summit Xl Bowl |
| gso_Cole_Hardware_Flower_Pot_1025 | plant_small | gso | keep | the vision check says it is not a plant_small (a vase) | Cole Hardware Flower Pot 1025 |
| gso_Cole_Hardware_Orchid_Pot_85 | plant_small | gso | keep | the vision check says it is not a plant_small; the vision check sees more than one object | Cole Hardware Orchid Pot 85 |
| gso_Down_To_Earth_Ceramic_Orchid_Pot_Asst_Blue | plant_small | gso | keep | the vision check says it is not a plant_small (a vase) | Down To Earth Ceramic Orchid Pot Asst Blue |
| gso_Down_To_Earth_Orchid_Pot_Ceramic_Lime | plant_small | gso | keep | the vision check says it is not a plant_small (a vase) | Down To Earth Orchid Pot Ceramic Lime |
| gso_Down_To_Earth_Orchid_Pot_Ceramic_Red | plant_small | gso | keep | the vision check says it is not a plant_small (a vase) | Down To Earth Orchid Pot Ceramic Red |
| gso_Ecoforms_Plant_Container_12_Pot_Nova | plant_small | gso | keep | the vision check says it is not a plant_small (a vase) | Ecoforms Plant Container 12 Pot Nova |
| gso_Ecoforms_Plant_Pot_GP9AAvocado | plant_small | gso | keep | the vision check says it is not a plant_small; the vision check sees more than one object; vision quality 2 (<= 2) | Ecoforms Plant Pot GP9AAvocado |
| gso_Ecoforms_Plant_Pot_GP9_SAND | plant_small | gso | keep | the vision check says it is not a plant_small; the vision check sees more than one object; vision quality 2 (<= 2) | Ecoforms Plant Pot GP9 SAND |
| gso_Ecoforms_Planter_Bowl_Cole_Hardware | plant_small | gso | keep | the vision check says it is not a plant_small (a bowl); the vision check sees more than one object | Ecoforms Planter Bowl Cole Hardware |
| gso_Ecoforms_Planter_Pot_GP12AAvocado | plant_small | gso | keep | the vision check sees more than one object | Ecoforms Planter Pot GP12AAvocado |
| gso_Ecoforms_Planter_Pot_QP6Ebony | plant_small | gso | keep | the vision check says it is not a plant_small (a vase) | Ecoforms Planter Pot QP6Ebony |
| gso_Ecoforms_Pot_Nova_6_Turquoise | plant_small | gso | keep | the vision check says it is not a plant_small (a vase) | Ecoforms Pot Nova 6 Turquoise |
| gso_Sapota_Threshold_4_Ceramic_Round_Planter_Red | plant_small | gso | keep | the vision check says it is not a plant_small (a vase); the vision check sees more than one object | Sapota Threshold 4 Ceramic Round Planter Red |
| infinigen_books_0 | books | generated | keep | vision quality 2 (<= 2) | Infinigen books (BookStackFactory, seed 0) |
| infinigen_bowl_0 | bowl | generated | keep | not a real manufactured product and vision quality 3 (< 4) | Infinigen bowl (BowlFactory, seed 0) |
| infinigen_pot_0 | plant_small | generated | keep | vision quality 2 (<= 2) | Infinigen pot (PlantContainerFactory, seed 0) |
| infinigen_books_1 | books | generated | keep | vision quality 2 (<= 2) | Infinigen books (BookStackFactory, seed 1) |
| infinigen_bowl_1 | bowl | generated | keep | not a real manufactured product and vision quality 3 (< 4) | Infinigen bowl (BowlFactory, seed 1) |
| infinigen_pot_1 | plant_small | generated | keep | not a real manufactured product and vision quality 3 (< 4) | Infinigen pot (PlantContainerFactory, seed 1) |
| infinigen_books_2 | books | generated | keep | not a real manufactured product and vision quality 3 (< 4) | Infinigen books (BookStackFactory, seed 2) |
| infinigen_bowl_2 | bowl | generated | keep | not a real manufactured product and vision quality 3 (< 4) | Infinigen bowl (BowlFactory, seed 2) |
| infinigen_pot_2 | plant_small | generated | keep | not a real manufactured product and vision quality 3 (< 4) | Infinigen pot (PlantContainerFactory, seed 2) |
| Rockingchair_01 | armchair | polyhaven | keep | the vision check says it is not a armchair (a chair) | Rockingchair 01 |
| chinese_stool | bar_stool | polyhaven | keep | the vision check says it is not a bar_stool (a chair) | Chinese Stool |
| metal_stool_03 | bar_stool | polyhaven | keep | the vision check says it is not a bar_stool (a chair) | Metal Stool 03 |
| GreenChair_01 | chair | polyhaven | keep | the vision check says it is not a chair (a armchair) | Green Chair 01 |
| chinese_armchair | office_chair | polyhaven | keep | the vision check says it is not a office_chair (a armchair) | Chinese Armchair |
| metal_stool_02 | ottoman | polyhaven | keep | the vision check says it is not a ottoman (a bar_stool) | Metal Stool 02 |
| round_wooden_table_01 | table_dining | polyhaven | keep | the vision check says it is not a table_dining (a side_table) | Round Wooden Table 01 |
| round_wooden_table_02 | table_dining | polyhaven | keep | the vision check says it is not a table_dining (a side_table) | Round Wooden Table 02 |
| vintage_cabinet_01 | wardrobe | polyhaven | keep | the vision check says it is not a wardrobe (a display_cabinet) | Vintage Cabinet 01 |
| hanging_picture_frame_01 | wall_art | polyhaven | keep | vision quality 2 (<= 2) | Hanging Picture Frame 01 |
| hanging_picture_frame_03 | wall_art | polyhaven | keep | the vision check sees more than one object | Hanging Picture Frame 03 |

## Models to remove (catalogue only; the files stay on the volume)

| id | type | source | status | reason | title |
|---|---|---|---|---|---|
| abo_B07DYV7WN2 | chair | abo | removed | the title names cup, not a chair | JC Home Bilbao Kids Recliner with Cup Holder and Headrest, M |
| infinigen_toilet_0 | toilet | generated | removed | a drawer, door or lid is open, or a part floats apart | Infinigen toilet (ToiletFactory, seed 0) |
| infinigen_kitchen_sink_0 | sink_kitchen | generated | removed | 0.76 x 0.62 x 0.51 m fits a sink_kitchen only with another axis up: the model lies on its side | Infinigen kitchen sink (SinkFactory, seed 0) |
| infinigen_oven_0 | stove | generated | removed | a product of known units 97% off a real stove (1.04 x 1.42 x 1.64 m): not a stove | Infinigen oven (OvenFactory, seed 0) |
| infinigen_beverage_fridge_0 | fridge | generated | removed | a product of known units 37% off a real fridge (1.04 x 1.34 x 1.18 m): not a fridge | Infinigen beverage fridge (BeverageFridgeFactory, seed 0) |
| infinigen_kitchen_sink_1 | sink_kitchen | generated | removed | 0.68 x 0.60 x 0.44 m fits a sink_kitchen only with another axis up: the model lies on its side | Infinigen kitchen sink (SinkFactory, seed 1) |
| infinigen_oven_1 | stove | generated | removed | a product of known units 41% off a real stove (0.94 x 1.38 x 1.37 m): not a stove | Infinigen oven (OvenFactory, seed 1) |
| infinigen_beverage_fridge_1 | fridge | generated | removed | proportions 0.94 x 1.31 x 1.03 m fit no real fridge (width (0.55, 0.95), depth (0.55, 0.8), height (0.8, 2.1)) | Infinigen beverage fridge (BeverageFridgeFactory, seed 1) |
| infinigen_kitchen_sink_2 | sink_kitchen | generated | removed | proportions 0.69 x 0.54 x 0.56 m fit no real sink_kitchen (width (0.45, 1.2), depth (0.4, 0.6), height (0.8, 1.3)) | Infinigen kitchen sink (SinkFactory, seed 2) |
| infinigen_oven_2 | stove | generated | removed | a product of known units 38% off a real stove (0.99 x 1.16 x 1.13 m): not a stove | Infinigen oven (OvenFactory, seed 2) |
| infinigen_beverage_fridge_2 | fridge | generated | removed | proportions 0.99 x 1.10 x 0.85 m fit no real fridge (width (0.55, 0.95), depth (0.55, 0.8), height (0.8, 2.1)) | Infinigen beverage fridge (BeverageFridgeFactory, seed 2) |
| abo_B073P1GB8K | wall_art | abo | removed | the vision check sees it lying on its side or upside down | Amazon Brand – Stone & Beam Contemporary Turquoise and Tan D |
| abo_B073P5Y9J1 | wall_art | abo | removed | the title says city: an outdoor piece | Amazon Brand – Rivet Modern Black and White Map of New York  |
| abo_B073P66TV3 | wall_art | abo | removed | the title says city: an outdoor piece | Amazon Brand – Rivet Modern Black and White Map of New York  |
| abo_B075HRC94H | wall_art | abo | removed | the title names bird, not a wall_art | Amazon Brand – Stone & Beam Modern Left-Facing Bird Line Dra |
| abo_B075HRFFRL | wall_art | abo | removed | the title says city: an outdoor piece | Rivet Modern Abstract City Skyscrapers on Canvas, 30"W, Mult |
| gso_Squirt_Strain_Fruit_Basket | basket | gso | removed | a product of known units 64% off a real basket (0.11 x 0.09 x 0.11 m): not a basket | Squirt Strain Fruit Basket |
| gso_Tag_Dishtowel_Basket_Weave_Red_18_x_26 | basket | gso | removed | a product of known units 178% off a real basket (0.17 x 0.23 x 0.03 m): not a basket | Tag Dishtowel Basket Weave Red 18 x 26 |
| gso_Central_Garden_Flower_Pot_Goo_425 | plant_small | gso | removed | the title says garden: an outdoor piece | Central Garden Flower Pot Goo 425 |
| gso_Ecoforms_Garden_Pot_GP16ATurquois | plant_small | gso | removed | the title says garden: an outdoor piece | Ecoforms Garden Pot GP16ATurquois |
| gso_Threshold_Tray_Rectangle_Porcelain | tray | gso | removed | the vision check sees it lying on its side or upside down | Threshold Tray Rectangle Porcelain |
| wooden_stool_02 | bar_stool | polyhaven | removed | proportions 0.27 x 0.18 x 0.18 m fit no real bar_stool (width (0.3, 0.6), depth (0.3, 0.7), height (0.55, 1.25)) | Wooden Stool 02 |
| steel_frame_shelves_01 | bookshelf | polyhaven | removed | a product of known units 983% off a real bookshelf (10.97 x 5.02 x 21.41 m): not a bookshelf | Steel Frame Shelves 01 |
| steel_frame_shelves_02 | bookshelf | polyhaven | removed | proportions 0.59 x 0.50 x 2.14 m fit no real bookshelf (width (0.6, 2.0), depth (0.25, 0.45), height (0.7, 2.5)) | Steel Frame Shelves 02 |
| steel_frame_shelves_03 | bookshelf | polyhaven | removed | a product of known units 56% off a real bookshelf (2.35 x 0.72 x 2.31 m): not a bookshelf | Steel Frame Shelves 03 |
| BarberShopChair_01 | chair | polyhaven | removed | a product of known units 98% off a real chair (0.76 x 1.33 x 1.49 m): not a chair | Barber Shop Chair 01 |
| WoodenChair_01 | chair | polyhaven | removed | a product of known units 84% off a real chair (0.69 x 0.66 x 2.27 m): not a chair | Wooden Chair 01 |
| GothicCabinet_01 | sideboard | polyhaven | removed | proportions 1.72 x 1.12 x 2.36 m fit no real sideboard (width (1.0, 2.4), depth (0.35, 0.55), height (0.6, 1.2)) | Gothic Cabinet 01 |
| chinese_cabinet | sideboard | polyhaven | removed | 1.26 x 0.55 x 2.87 m fits a sideboard only with another axis up: the model lies on its side | Chinese Cabinet |
| chinese_commode | sideboard | polyhaven | removed | a product of known units 107% off a real sideboard (4.49 x 1.17 x 2.02 m): not a sideboard | Chinese Commode |
| gallinera_table | table_dining | polyhaven | removed | a product of known units 31% off a real table_dining (0.83 x 0.52 x 0.49 m): not a table_dining | Gallinera Table |
| wicker_basket_02 | basket | polyhaven | removed | a drawer, door or lid is open, or a part floats apart | Wicker Basket 02 |
| brass_candleholders | candle | polyhaven | removed | a product of known units 127% off a real candle (1.05 x 0.36 x 0.84 m): not a candle | Brass Candleholders |
| wall_clock | clock | polyhaven | removed | the vision check sees it lying on its side or upside down | Wall Clock |
| bronze_whale_statue | sculpture | polyhaven | removed | a product of known units 47% off a real sculpture (0.93 x 1.37 x 1.07 m): not a sculpture | Bronze Whale Statue |
| gothic_statue | sculpture | polyhaven | removed | a product of known units 69% off a real sculpture (1.48 x 1.56 x 1.74 m): not a sculpture | Gothic Statue |
| horse_head | sculpture | polyhaven | removed | the title names horse, not a sculpture | Horse Head |
| hanging_picture_frame_02 | wall_art | polyhaven | removed | the vision check sees it lying on its side or upside down | Hanging Picture Frame 02 |

## Models to fix

| id | type | source | fixes | why |
|---|---|---|---|---|
| abo_B07BWJCPSN | sofa_corner | abo | {"front_quarter_turns": 3} | its front is on the wrong side for a sofa_corner (width along the front): turned 270 deg (to the geometric front -X) |
| infinigen_toilet_1 | toilet | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2 or Infinigen): no real product; 4 part(s) stick out of the main body (+z, -x, up to 0.26 m): an ope |
| infinigen_toilet_2 | toilet | generated | {"front_quarter_turns": 1} | generated (TRELLIS.2 or Infinigen): no real product; 4 part(s) stick out of the main body (+z, -x, up to 0.29 m): an ope |
| vintage_day_bed | bed_single | polyhaven | {"front_quarter_turns": 1} | its front is on the wrong side for a bed_single (width along the front): turned 90 deg (side unknown: the vision check c |
