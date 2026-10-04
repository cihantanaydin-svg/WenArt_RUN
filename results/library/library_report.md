# Furniture library (docs/milestone7.md §7, docs/milestone8.md §2)

Contains information from Objaverse 1.0 (https://huggingface.co/datasets/allenai/objaverse, revision 21e4e14), which is made available under the ODC Attribution License (ODC-By 1.0, https://opendatacommons.org/licenses/by/1-0/). Every object keeps its own licence, as declared by its uploader and not verified by WenArt_RUN (CC0 1.0 and CC BY 4.0 unflagged, every other licence flagged: docs/milestone8.md §2): check it before commercial use. This file is licensed ODC-By 1.0, not MIT.

Contains 3D models and product data from Amazon Berkeley Objects (https://amazon-berkeley-objects.s3.amazonaws.com/index.html), (c) Amazon.com, licensed CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Credit for the data, including all images and 3D models: Amazon.com; for building the dataset: Matthieu Guillaumin, Thomas Dideriksen, Kenan Deng, Himanshu Arora (Amazon.com), Jasmine Collins and Jitendra Malik (UC Berkeley). Changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched.

Generated models (docs/milestone8.md §3): made by TRELLIS.2-4B (microsoft/TRELLIS.2-4B, MIT) from Z-Image-Turbo product images; marked `generated`, no third-party credit.

Objaverse: [allenai/objaverse](https://huggingface.co/datasets/allenai/objaverse) @ `21e4e14` (ODC-By-1.0). Licence strings and metadata field names of objaverse.yaml verified on the pod: yes. Every licence is taken (docs/milestone8.md §2); not CC0 / CC BY 4.0 -> licence_flag.

## Sources

| Source | Survey file | Candidates | With GLB | Ready | Judged by both | Accepted | In catalogue |
|---|---|---|---|---|---|---|---|
| abo | survey_abo.json | 828 | 828 | 508 | 508 | 345 | 345 |
| objaverse | survey.json | 396 | 396 | 316 | 316 | 77 | 77 |
| generated | survey_generated.json | 176 | 176 | 172 | 172 | 130 | 130 |

## Steps

| Step | Objects |
|---|---|
| Objaverse: LVIS objects in the mapped categories | 1498 |
| Objaverse: licence CC0 or CC BY 4.0 (metadata) | 1370 |
| Objaverse: other licences (taken, flagged) | 128 |
| Objaverse: past the metadata prefilter (credit, faces, size) | 984 |
| Candidates of every source (downloaded; textured or vertex-coloured) | 1400 |
| Rendered (thumbnails) | 1400 |
| Ready for judging (unit and type resolved) | 996 |
| of which normalised by type (model units unknown) | 323 |
| Judged by both models | 996 |
| Accepted | 552 |
| In catalog_library.json | 552 |

## Per type (Objaverse bed candidates are split into bed_single / bed_double after the unit guess)

| Type | Source | LVIS | Candidates | Ready | Accepted | In catalogue |
|---|---|---|---|---|---|---|
| armchair | abo | – | 40 | 24 | 14 | 14 |
| armchair | objaverse | 97 | 24 | 21 | 6 | 6 |
| bathtub | objaverse | 30 | 26 | 17 | 1 | 1 |
| bathtub | generated | – | 18 | 16 | 12 | 12 |
| bed_double | abo | – | 40 | 24 | 18 | 18 |
| bed_double | objaverse | – | 0 | 11 | 2 | 2 |
| bed_double|bed_single | objaverse | 53 | 22 | 0 | 0 | 0 |
| bed_single | abo | – | 12 | 12 | 7 | 7 |
| bed_single | objaverse | – | 0 | 11 | 2 | 2 |
| bed_single | generated | – | 10 | 10 | 10 | 10 |
| bookshelf | abo | – | 40 | 24 | 13 | 13 |
| bookshelf | objaverse | 103 | 24 | 20 | 7 | 7 |
| bowl | generated | – | 10 | 10 | 9 | 9 |
| chair | abo | – | 40 | 24 | 13 | 13 |
| chair | objaverse | 453 | 24 | 21 | 7 | 7 |
| cushion | abo | – | 40 | 24 | 20 | 20 |
| desk | abo | – | 40 | 24 | 18 | 18 |
| desk | objaverse | 76 | 24 | 20 | 2 | 2 |
| dresser | abo | – | 40 | 24 | 18 | 18 |
| floor_lamp | abo | – | 40 | 24 | 12 | 12 |
| floor_lamp | objaverse | 79 | 21 | 15 | 6 | 6 |
| floor_lamp | generated | – | 2 | 2 | 2 | 2 |
| fridge | objaverse | 55 | 33 | 24 | 5 | 5 |
| fridge | generated | – | 14 | 14 | 8 | 8 |
| mirror | abo | – | 40 | 24 | 17 | 17 |
| nightstand | abo | – | 40 | 24 | 18 | 18 |
| plant | abo | – | 40 | 24 | 0 | 0 |
| plant_small | generated | – | 10 | 10 | 10 | 10 |
| potted_plant | objaverse | 81 | 24 | 23 | 6 | 6 |
| potted_plant | generated | – | 14 | 14 | 12 | 12 |
| rug | abo | – | 40 | 24 | 20 | 20 |
| shower | generated | – | 18 | 18 | 6 | 6 |
| side_table | abo | – | 40 | 24 | 20 | 20 |
| sink_kitchen | generated | – | 18 | 17 | 11 | 11 |
| sofa | abo | – | 40 | 24 | 17 | 17 |
| sofa | objaverse | 81 | 24 | 18 | 1 | 1 |
| sofa | generated | – | 2 | 2 | 2 | 2 |
| stove | objaverse | 35 | 29 | 20 | 3 | 3 |
| stove | generated | – | 10 | 9 | 8 | 8 |
| table_coffee | abo | – | 40 | 24 | 15 | 15 |
| table_coffee | objaverse | 51 | 18 | 16 | 5 | 5 |
| table_dining | abo | – | 40 | 24 | 18 | 18 |
| table_dining | objaverse | 70 | 16 | 10 | 2 | 2 |
| table_lamp | abo | – | 40 | 24 | 20 | 20 |
| toilet | objaverse | 111 | 40 | 24 | 8 | 8 |
| toilet | generated | – | 14 | 14 | 7 | 7 |
| tv_unit | abo | – | 40 | 24 | 20 | 20 |
| vase | abo | – | 40 | 24 | 20 | 20 |
| wall_art | abo | – | 40 | 24 | 17 | 17 |
| wardrobe | abo | – | 16 | 16 | 10 | 10 |
| wardrobe | objaverse | 97 | 24 | 23 | 6 | 6 |
| wardrobe | generated | – | 6 | 6 | 4 | 4 |
| washbasin | objaverse | 26 | 23 | 22 | 8 | 8 |
| washbasin | generated | – | 12 | 12 | 11 | 11 |
| washing_machine | generated | – | 18 | 18 | 18 | 18 |

## Refusals by reason (first failed rule per object)

| Step | Code | Reason | Objects | Sources |
|---|---|---|---|---|
| survey | face_count | face count outside 2k-150k (fixture categories: 800-400k, docs/milestone9.md §2.2) | 483 | objaverse 483 |
| survey | glb_size | GLB larger than the source's limit (Objaverse 40 MB, ABO 60 MB) | 73 | abo 42, objaverse 31 |
| survey | not_generated | not_generated | 125 | generated 125 |
| survey | size_range | box outside the resolved type's size range (units known: never normalised) | 528 | abo 528 |
| survey | untextured | no image texture and no vertex colours | 61 | objaverse 61 |
| survey | not_selected | below the candidates per type (rank, or the pick order) | 4463 |  |
| thumbnails | over_candidate_limit | over the candidates of its source and type after the bed split | 342 | abo 320, objaverse 22 |
| thumbnails | unit_none | no unit factor fits and the box proportions (footprint, height / width) are outside the type's ranges | 62 | objaverse 58, generated 4 |
| accept | front_not_agreed | front not agreed (judges and geometry or the documented front) | 89 | abo 4, objaverse 73, generated 12 |
| accept | no_common_style | no style both judges name | 30 | abo 19, objaverse 5, generated 6 |
| accept | not_decor_type | not the decor type (a judge; a planter must hold a plant) | 26 | abo 26 |
| accept | not_single | not a single object (a judge) | 5 | objaverse 5 |
| accept | over_type_limit | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1) | 113 | abo 56, objaverse 55, generated 2 |
| accept | quality | photoreal quality below 4 (a judge) | 168 | abo 54, objaverse 92, generated 22 |
| accept | type_mismatch | not the furniture type (a judge) | 13 | abo 4, objaverse 9 |

## Licence values seen (Objaverse metadata field `license`)

| Value | Objects | Licence | Flag |
|---|---|---|---|
| `by` | 1369 | CC-BY-4.0 | – |
| `by-sa` | 77 | CC-BY-SA-4.0 | share_alike |
| `by-nc` | 35 | CC-BY-NC-4.0 | non_commercial |
| `by-nc-sa` | 16 | CC-BY-NC-SA-4.0 | non_commercial |
| `cc0` | 1 | CC0 | – |

## LVIS categories

Found: `armchair` 97, `armoire` 58, `bathtub` 30, `bed` 53, `bookcase` 103, `chair` 453, `coffee_table` 51, `desk` 76, `dining_table` 70, `flowerpot` 81, `lamp` 79, `refrigerator` 55, `sink` 26, `sofa` 81, `stove` 35, `toilet` 111, `wardrobe` 39.
Missing (a warning: their types stay parametric): `chest_of_drawers_(furniture)`, `nightstand`.

- `chest_of_drawers_(furniture)`: names in the file sharing a word: `drawer` (an alternate needs a reason in objaverse.yaml).
- `nightstand`: names in the file sharing a word: `nightshirt` (an alternate needs a reason in objaverse.yaml).


## ABO mapping (abo.yaml rules; units known: metres)

| Type | Mapped | In the size range | Candidates | Not selected |
|---|---|---|---|---|
| armchair | 580 | 560 | 40 | 510 |
| bed_double | 161 | 144 | 40 | 104 |
| bed_single | 27 | 12 | 12 | 0 |
| bookshelf | 48 | 41 | 40 | 1 |
| chair | 430 | 367 | 40 | 323 |
| cushion | 195 | 195 | 40 | 149 |
| desk | 146 | 101 | 40 | 61 |
| dresser | 53 | 46 | 40 | 6 |
| floor_lamp | 101 | 76 | 40 | 36 |
| mirror | 137 | 128 | 40 | 87 |
| nightstand | 82 | 76 | 40 | 36 |
| plant | 185 | 139 | 40 | 99 |
| rug | 861 | 861 | 40 | 814 |
| side_table | 136 | 121 | 40 | 81 |
| sofa | 962 | 748 | 40 | 695 |
| table_coffee | 152 | 143 | 40 | 103 |
| table_dining | 54 | 46 | 40 | 6 |
| table_lamp | 242 | 242 | 40 | 201 |
| tv_unit | 68 | 57 | 40 | 17 |
| vase | 54 | 54 | 40 | 14 |
| wall_art | 639 | 633 | 40 | 593 |
| wardrobe | 21 | 16 | 16 | 0 |

Product types with a 3D model left unmapped: HOME_FURNITURE_AND_DECOR 387, STOOL_SEATING 340, OTTOMAN 288, HEADBOARD 206, LIGHT_FIXTURE 195, TABLE 161, CHAIR 132, CABINET 112, HOME 92, PILLOW 88, SHELF 57, BENCH 39, FURNITURE_COVER 34, ELECTRIC_FAN 29, SPORTING_GOODS 28, CLOTHES_RACK 24, STORAGE_BOX 23, FREESTANDING_SHELTER 20, FLAT_SCREEN_DISPLAY_MOUNT 18, CURTAIN 17, MATTRESS 17, MULTIPORT_HUB 16, PROFESSIONAL_HEALTHCARE 16, AUTO_ACCESSORY 14, BEAN_BAG_CHAIR 14, FURNITURE 14, AIR_CONDITIONER 13, HOME_BED_AND_BATH 13, OUTDOOR_LIVING 13, LADDER 11.

## Licence flags (catalogue)

| Licence | Flag | Models |
|---|---|---|
| CC-BY-4.0 | – | 415 |
| CC-BY-NC-4.0 | non_commercial | 4 |
| CC-BY-SA-4.0 | share_alike | 3 |
| generated (TRELLIS.2-4B, MIT) | – | 130 |

## Style coverage

Models per type and style family: library + Poly Haven (`neutral` counts for every family; beds with a mattress or as a bed frame with a deck). `–` = no model: refit builds the parametric mesh for that pair (or a generated model fills it, docs/milestone8.md §3).

| Type | scandinavian | japandi | modern minimal | minimal | modern | industrial | mediterranean | classic | rustic |
|---|---|---|---|---|---|---|---|---|---|
| bed_single | 11+0 | 10+0 | 18+0 | 14+0 | 13+0 | 2+0 | – | 1+0 | – |
| bed_double | 6+0 | 4+0 | 16+0 | 11+0 | 12+0 | 2+0 | – | 0+1 | 1+0 |
| sofa | 5+0 | 2+0 | 11+0 | 8+0 | 15+0 | – | – | 5+3 | – |
| armchair | 5+0 | 2+0 | 9+1 | 7+1 | 12+2 | 2+0 | 2+0 | 10+1 | 2+0 |
| table_dining | 14+0 | 8+0 | 14+0 | 14+0 | 15+0 | 5+0 | 1+0 | 1+0 | 5+3 |
| table_coffee | 8+0 | 13+0 | 18+0 | 15+0 | 16+2 | 5+0 | 1+0 | 2+1 | 3+1 |
| desk | 11+0 | 6+0 | 18+0 | 8+0 | 13+0 | 8+2 | – | – | 1+1 |
| chair | 6+0 | 5+0 | 8+0 | 7+0 | 10+1 | 3+0 | 1+0 | 6+1 | 3+2 |
| wardrobe | 12+0 | 2+0 | 15+0 | 15+0 | 13+0 | 3+0 | 2+0 | 6+0 | 3+0 |
| fridge | – | – | 12+0 | 8+0 | 11+0 | 1+0 | – | 1+0 | – |
| stove | 1+1 | 0+1 | 5+1 | 4+1 | 8+1 | 2+1 | 0+1 | 2+1 | 0+1 |
| washbasin | 3+0 | 1+0 | 19+0 | 19+0 | 18+0 | – | – | – | – |
| toilet | – | – | 15+0 | 15+0 | 15+0 | – | – | – | – |
| bathtub | – | – | 13+0 | 13+0 | 13+0 | – | – | – | – |
| tv_unit | 5+0 | 14+0 | 12+1 | 10+1 | 10+1 | 1+1 | – | 1+0 | 3+1 |
| bookshelf | 7+1 | 3+1 | 16+1 | 13+1 | 12+1 | 5+0 | 1+0 | 3+0 | 1+2 |
| nightstand | 7+1 | 5+1 | 17+1 | 15+1 | 10+1 | – | – | 0+1 | 2+1 |
| dresser | 7+0 | 5+0 | 14+0 | 11+0 | 13+0 | 3+0 | 2+0 | 3+2 | 4+0 |
| side_table | 7+0 | 7+0 | 12+0 | 12+0 | 11+0 | 7+0 | 2+0 | 3+0 | 5+0 |
| floor_lamp | 5+0 | – | 9+0 | 9+0 | 12+0 | 5+0 | – | 5+0 | – |
| potted_plant | 12+0 | 9+0 | 14+0 | 15+0 | 13+0 | 6+0 | 8+0 | 6+0 | 8+0 |

Parametric: 34 of 189 type/family pairs (bed_single/mediterranean, bed_single/rustic, bed_double/mediterranean, sofa/industrial, sofa/mediterranean, sofa/rustic, desk/mediterranean, desk/classic, fridge/scandinavian, fridge/japandi, fridge/mediterranean, fridge/rustic, washbasin/industrial, washbasin/mediterranean, washbasin/classic, washbasin/rustic, toilet/scandinavian, toilet/japandi, toilet/industrial, toilet/mediterranean, toilet/classic, toilet/rustic, bathtub/scandinavian, bathtub/japandi, bathtub/industrial, bathtub/mediterranean, bathtub/classic, bathtub/rustic, tv_unit/mediterranean, nightstand/industrial, nightstand/mediterranean, floor_lamp/japandi, floor_lamp/mediterranean, floor_lamp/rustic).

## Beds

| Id | Type | Source | Mattress | Bed frame | Deck (m) |
|---|---|---|---|---|---|
| `abo_B0718WYQ8D` | bed_single | abo | True | False | – |
| `abo_B073WR319C` | bed_single | abo | True | False | – |
| `abo_B075Y184L3` | bed_single | abo | False | True | 0.3744 |
| `abo_B07H8V14CZ` | bed_single | abo | True | False | – |
| `abo_B07H8V7MQS` | bed_single | abo | True | False | – |
| `abo_B0856FL9HR` | bed_single | abo | True | False | – |
| `abo_B086TFXK75` | bed_single | abo | True | False | – |
| `gen_bed_single_classic_1_dbac0f10` | bed_single | generated | True | False | – |
| `gen_bed_single_industrial_1_9f087076` | bed_single | generated | True | False | – |
| `gen_bed_single_japandi_1_35dff430` | bed_single | generated | True | False | – |
| `gen_bed_single_mediterranean_1_c9d313b4` | bed_single | generated | True | False | – |
| `gen_bed_single_mediterranean_2_8f745c9f` | bed_single | generated | True | False | – |
| `gen_bed_single_minimal_1_738c07ed` | bed_single | generated | True | False | – |
| `gen_bed_single_modern_1_cb4f07bd` | bed_single | generated | True | False | – |
| `gen_bed_single_modern_minimal_1_5c05505b` | bed_single | generated | True | False | – |
| `gen_bed_single_rustic_1_db9b30c6` | bed_single | generated | True | False | – |
| `gen_bed_single_scandinavian_1_8060783a` | bed_single | generated | True | False | – |
| `objaverse_6eb4212e70b941a3bd2db196a47828b9` | bed_single | objaverse | True | False | – |
| `objaverse_b547d81073b64d3e97200fd3ae9a74af` | bed_single | objaverse | True | False | – |
| `abo_B0154VUESC` | bed_double | abo | True | False | – |
| `abo_B01M0ZVGCQ` | bed_double | abo | True | False | – |
| `abo_B01N6AQX0A` | bed_double | abo | True | False | – |
| `abo_B071FJR4FW` | bed_double | abo | True | False | – |
| `abo_B071W2SCTJ` | bed_double | abo | True | False | – |
| `abo_B072PWGSZL` | bed_double | abo | True | False | – |
| `abo_B075QDMWTP` | bed_double | abo | True | False | – |
| `abo_B075Z8767S` | bed_double | abo | True | False | – |
| `abo_B07B4YNHSN` | bed_double | abo | True | False | – |
| `abo_B07B4Z9Q3S` | bed_double | abo | True | False | – |
| `abo_B07BBWMPJM` | bed_double | abo | True | False | – |
| `abo_B07GFDZW5W` | bed_double | abo | True | False | – |
| `abo_B07GFFR415` | bed_double | abo | True | False | – |
| `abo_B07L1DDXLR` | bed_double | abo | True | False | – |
| `abo_B084ZBDPG5` | bed_double | abo | True | False | – |
| `abo_B084ZBX1YH` | bed_double | abo | True | False | – |
| `abo_B086TGFT35` | bed_double | abo | True | False | – |
| `abo_B08FTN8KHY` | bed_double | abo | True | False | – |
| `objaverse_08f7f65edfea417b8ed9ca748381e507` | bed_double | objaverse | True | False | – |
| `objaverse_5d3a99865ac84d8a8bf06b263aa5bb55` | bed_double | objaverse | True | False | – |

## Catalogue

| Type | Source | Id | Title | Author | Licence | Flag | Styles | Front | Quality | W x D x H (m) | Unit |
|---|---|---|---|---|---|---|---|---|---|---|---|
| bed_single | abo | `abo_B0718WYQ8D` | Amazon Brand - Movian Aveyron Single Bed Frame, 195 x 100 x 80cm, Pink | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.998 x 1.96 x 0.805 | x1 |
| bed_single | abo | `abo_B073WR319C` | AmazonBasics Foldable, 14" Metal Platform Bed Frame with Tool-Free Assembly, No Box Spring Needed - Twin | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal | -Y (high) | 4/4 | 1.02 x 1.91 x 0.64 | x1 |
| bed_single | abo | `abo_B075Y184L3` | AmazonBasics Faux Leather Upholstered Platform Bed Frame with Wooden Slats, Twin | Amazon.com | CC-BY-4.0 | – | modern minimal | -Y (high) | 5/4 | 1.04 x 2.15 x 1.05 | x1 |
| bed_single | abo | `abo_B07H8V14CZ` | Movian Moselle. | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/4 | 0.99 x 2.14 x 0.92 | x1 |
| bed_single | abo | `abo_B07H8V7MQS` | Movian Moselle. | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 4/4 | 0.99 x 2.14 x 0.92 | x1 |
| bed_single | abo | `abo_B0856FL9HR` | Amazon Brand – Rivet Modern Solid Pine Wood Platform Bed, Twin, 38.39"W, Antique Espresso | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 4/4 | 0.961 x 1.9 x 0.616 | x1 |
| bed_single | abo | `abo_B086TFXK75` | AmazonBasics Metal Bed with Modern Industrial Design Headboard - 14 Inch Height for Under-Bed Storage - Wood Slats - Easy Assemble, Twin | Amazon.com | CC-BY-4.0 | – | modern minimal, industrial | -Y (high) | 4/4 | 0.991 x 1.93 x 0.967 | x1 |
| bed_single | generated | `gen_bed_single_classic_1_dbac0f10` | Generated classic bed single (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | classic | -Y (high) | 5/5 | 1.19 x 1.68 x 1.08 | x1.67513 |
| bed_single | generated | `gen_bed_single_industrial_1_9f087076` | Generated industrial bed single (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, industrial | -Y (high) | 4/4 | 1.1 x 1.82 x 0.984 | x1.81967 |
| bed_single | generated | `gen_bed_single_japandi_1_35dff430` | Generated japandi bed single (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/4 | 1.26 x 1.59 x 0.671 | x1.58327 |
| bed_single | generated | `gen_bed_single_mediterranean_1_c9d313b4` | Generated mediterranean bed single (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 4/4 | 1.21 x 1.65 x 0.857 | x1.64619 |
| bed_single | generated | `gen_bed_single_mediterranean_2_8f745c9f` | Generated mediterranean bed single (2) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 4/4 | 1.08 x 1.85 x 0.953 | x1.84679 |
| bed_single | generated | `gen_bed_single_minimal_1_738c07ed` | Generated minimal bed single (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 4/4 | 1.05 x 1.9 x 0.876 | x1.8999 |
| bed_single | generated | `gen_bed_single_modern_1_cb4f07bd` | Generated modern bed single (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | japandi, modern minimal, modern | -Y (high) | 4/4 | 1.17 x 1.71 x 0.81 | x1.70748 |
| bed_single | generated | `gen_bed_single_modern_minimal_1_5c05505b` | Generated modern minimal bed single (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal | -Y (high) | 4/4 | 1.29 x 1.57 x 0.751 | x1.56216 |
| bed_single | generated | `gen_bed_single_rustic_1_db9b30c6` | Generated rustic bed single (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | scandinavian, japandi, modern minimal, minimal, modern | -X (high) | 5/4 | 1.17 x 1.71 x 0.876 | x1.70677 |
| bed_single | generated | `gen_bed_single_scandinavian_1_8060783a` | Generated scandinavian bed single (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/4 | 1.24 x 1.62 x 0.715 | x1.61485 |
| bed_single | objaverse | `objaverse_6eb4212e70b941a3bd2db196a47828b9` | Lowpoly Bed | Mohamed199 | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -X (high) | 4/4 | 1.11 x 1.8 x 0.691 | x0.00535266 |
| bed_single | objaverse | `objaverse_b547d81073b64d3e97200fd3ae9a74af` | Bed - Sample | Mifu Saja | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 4/4 | 1 x 2.11 x 0.918 | x0.01 |
| bed_double | abo | `abo_B0154VUESC` | Amazon Brand - Movian Loue Bed Frame with Headboard, 160 x 200cm, White/Light Brown Oak-Effect | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 1.72 x 2.06 x 0.8 | x1 |
| bed_double | abo | `abo_B01M0ZVGCQ` | Movian Belaya | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal | -Y (high) | 4/4 | 1.45 x 1.95 x 0.629 | x1 |
| bed_double | abo | `abo_B01N6AQX0A` | Intex Premaire Luchtbed met Fiber Tech-technologie, nieuwe geïntegreerde elektrische pomp met gegevens en USB, PVC, grijs, 152 x 203 x 46 cm | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 1.52 x 2.04 x 0.46 | x1 |
| bed_double | abo | `abo_B071FJR4FW` | Amazon Brand – Stone & Beam Glenwood Industrial Metal Accent Bed, Queen, 84.5"L, Oak | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/4 | 1.63 x 2.11 x 1.42 | x1 |
| bed_double | abo | `abo_B071W2SCTJ` | Amazon Brand – Stone & Beam Glenwood Industrial Metal Accent Bed, King, 86"L, Oak | Amazon.com | CC-BY-4.0 | – | minimal, modern | -Y (high) | 5/4 | 1.76 x 2.22 x 1.49 | x1 |
| bed_double | abo | `abo_B072PWGSZL` | Amazon Brand – Rivet Ventura Mid-Century Louvered Queen Bed, 86"L, Cherry | Amazon.com | CC-BY-4.0 | – | modern minimal, modern | -Y (high) | 4/4 | 1.6 x 2.18 x 1.27 | x1 |
| bed_double | abo | `abo_B075QDMWTP` | Amazon Brand – Rivet Payton Mid-Century Modern Tufted King Bed with Headboard, 82" W, Natural | Amazon.com | CC-BY-4.0 | – | modern minimal | -Y (high) | 5/4 | 2.04 x 2.38 x 1.52 | x1 |
| bed_double | abo | `abo_B075Z8767S` | Amazon Brand – Stone & Beam Bateman Casual Rustic Wood Platform Bed Frame with Tall Headboard, King, 81"W, Brown | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/4 | 1.7 x 2.28 x 1.42 | x1 |
| bed_double | abo | `abo_B07B4YNHSN` | Amazon Brand – Stone & Beam Tisbury Nailhead Trim Queen Bed, 66"W, Fresh Pewter | Amazon.com | CC-BY-4.0 | – | modern minimal | -Y (high) | 4/4 | 1.7 x 2.33 x 1.42 | x1 |
| bed_double | abo | `abo_B07B4Z9Q3S` | Stone & Beam Prudence Tufted King Bed, 84"W, Spinnsol Cocoa | Amazon.com | CC-BY-4.0 | – | modern | -Y (high) | 5/5 | 1.7 x 2.39 x 1.43 | x1 |
| bed_double | abo | `abo_B07BBWMPJM` | Amazon Brand - Movian Corona Double Bed, 4 ft 6, High Foot End Bed Frame, Solid Pine Wood | Amazon.com | CC-BY-4.0 | – | scandinavian, rustic | -Y (high) | 4/4 | 1.49 x 2.07 x 1.1 | x1 |
| bed_double | abo | `abo_B07GFDZW5W` | Movian Havel | Amazon.com | CC-BY-4.0 | – | modern minimal, modern | -Y (high) | 5/4 | 1.62 x 1.96 x 0.8 | x1 |
| bed_double | abo | `abo_B07GFFR415` | Amazon Brand - Movian Constance Lift-Up Double Bed Frame with Storage, 190 x 140 x 31.5cm, Light Brown Oak-Effect | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal | -Y (high) | 4/4 | 1.4 x 1.9 x 0.561 | x1 |
| bed_double | abo | `abo_B07L1DDXLR` | Amazon Brand - Solimo Aquilla Engineered Wood Queen Bed (Wenge Finish) | Amazon.com | CC-BY-4.0 | – | modern minimal, modern | -Y (high) | 4/4 | 1.58 x 2.07 x 0.823 | x1 |
| bed_double | abo | `abo_B084ZBDPG5` | Amazon Brand – Stone & Beam Rustic Solid Pine Bed with Headboard, King, 81.89"W, Gray | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 1.67 x 2.13 x 1.25 | x1 |
| bed_double | abo | `abo_B084ZBX1YH` | Amazon Brand – Stone & Beam Rustic Solid Pine Platform Bed, Queen, 63.15"W, Gray | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal | -Y (high) | 4/4 | 1.6 x 2.11 x 0.51 | x1 |
| bed_double | abo | `abo_B086TGFT35` | AmazonBasics Solid Platform Bed - Rustic Finish - No Box Spring Needed - Strong Wood Slat Support, Queen | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/4 | 1.54 x 2.02 x 0.431 | x1 |
| bed_double | abo | `abo_B08FTN8KHY` | Amazon Brand - Solimo Senna Metal Glossy King Bed (Black) | Amazon.com | CC-BY-4.0 | – | modern minimal, industrial | -Y (high) | 4/4 | 1.88 x 2.04 x 0.94 | x1 |
| bed_double | objaverse | `objaverse_08f7f65edfea417b8ed9ca748381e507` | Bed | Ambriel | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -X (high) | 5/4 | 2.43 x 2.12 x 0.9 | x0.001 |
| bed_double | objaverse | `objaverse_5d3a99865ac84d8a8bf06b263aa5bb55` | Old Bed | barism09 | CC-BY-4.0 | – | industrial | -Y (high) | 4/4 | 1.47 x 2.55 x 1.4 | x0.01 |
| sofa | abo | `abo_B0714QGC72` | Amazon Brand – Stone & Beam Bradbury Chesterfield Tufted Leather Sofa Couch, 92.9"W, Cognac | Amazon.com | CC-BY-4.0 | – | classic | -Y (high) | 5/5 | 2.37 x 0.989 x 0.76 | x1 |
| sofa | abo | `abo_B071FMSSWB` | Amazon Brand – Stone & Beam Hoffman Down-Filled Performance Fabric Loveseat Sofa, 79"W, Ecru | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 1.75 x 1.09 x 0.875 | x1 |
| sofa | abo | `abo_B071J7Q3J4` | Amazon Brand – Stone & Beam Bradbury Chesterfield Tufted Sofa Couch, 92.9"W, Hemp | Amazon.com | CC-BY-4.0 | – | classic | -Y (high) | 5/5 | 2.69 x 1.08 x 0.847 | x1 |
| sofa | abo | `abo_B072555T67` | Marchio Amazon - Movian Ackan - Divano a 3 posti, 209 x 87 x 80 cm, grigio chiaro | Amazon.com | CC-BY-4.0 | – | modern minimal, modern | -Y (high) | 4/5 | 2.1 x 0.849 x 0.795 | x1 |
| sofa | abo | `abo_B07263589M` | Amazon Brand – Stone & Beam Bradbury Chesterfield Tufted Loveseat Sofa Couch, 78.7"W, Navy | Amazon.com | CC-BY-4.0 | – | classic | -Y (high) | 5/5 | 1.99 x 1.08 x 0.833 | x1 |
| sofa | abo | `abo_B075X2WNRP` | Amazon Brand – Rivet Aiden Tufted Mid-Century Leather Bench Seat Sofa, Without Side Pillows, 74"W, Cognac | Amazon.com | CC-BY-4.0 | – | modern | -Y (high) | 4/5 | 1.92 x 0.924 x 0.825 | x1 |
| sofa | abo | `abo_B075X2X4GY` | Amazon Brand – Rivet Uptown Mid-Century Velvet Tufted Customizable Daybed Sofa, 78"W, Dove Grey &amp; Brass | Amazon.com | CC-BY-4.0 | – | modern minimal, modern | -Y (high) | 4/5 | 1.98 x 0.686 x 0.635 | x1 |
| sofa | abo | `abo_B075X4JB3K` | Amazon Brand – Rivet Eva Tufted Mid-Century Velvet Down-Filled Loveseat, 60.5"W, Hunter Green | Amazon.com | CC-BY-4.0 | – | classic | -Y (high) | 5/5 | 1.54 x 0.895 x 0.768 | x1 |
| sofa | abo | `abo_B07B4FW7H5` | Amazon Brand – Stone & Beam Andover Studio Sofa Couch, 78"W, Driftwood Leather | Amazon.com | CC-BY-4.0 | – | modern minimal, modern | -Y (high) | 5/5 | 1.97 x 0.923 x 0.863 | x1 |
| sofa | abo | `abo_B07BWJCBY2` | Amazon Brand – Stone & Beam Bradbury Chesterfield Tufted Leather Loveseat Sofa Couch, 78.7"W, Black | Amazon.com | CC-BY-4.0 | – | classic | -Y (high) | 5/5 | 2.05 x 0.944 x 0.779 | x1 |
| sofa | abo | `abo_B07HZ5P7P9` | Amazon Brand – Stone & Beam Bagley Sectional Component, Left-Facing Loveseat, Fabric, 52"W, Linen | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 4/5 | 1.39 x 0.991 x 0.989 | x1 |
| sofa | abo | `abo_B07HZ6GJC2` | Amazon Brand – Stone & Beam Bagley Sectional Component, Right Facing Loveseat, Fabric, 52"W, Linen | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 4/5 | 1.39 x 0.991 x 0.989 | x1 |
| sofa | abo | `abo_B07HZ6HHFF` | Amazon Brand – Stone & Beam Bagley Sectional Component, Armless Loveseat, Fabric, 44"W, Linen | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 4/5 | 1.24 x 0.951 x 1.01 | x1 |
| sofa | abo | `abo_B07HZ6X7ZF` | Amazon Brand – Stone & Beam Bagley Sectional Component, Left-Facing Sofa Chaise, Fabric, 41"W, Linen | Amazon.com | CC-BY-4.0 | – | modern | -Y (high) | 5/5 | 2.24 x 1.11 x 1.03 | x1 |
| sofa | abo | `abo_B07HZ72L2H` | Amazon Brand – Stone & Beam Bagley Sectional Component, Right-Facing Sofa, Fabric, 75"W, Linen | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 4/5 | 1.96 x 1.03 x 0.946 | x1 |
| sofa | abo | `abo_B07K9PMZJL` | Amazon Brand - Movian Dyvran 3-Seater Upholstered Sofa, 197 x 83 x 83 cm, Stain-Resistant Polyester, Dust Blue | Amazon.com | CC-BY-4.0 | – | scandinavian, modern | -Y (high) | 4/4 | 1.97 x 0.83 x 0.83 | x1 |
| sofa | abo | `abo_B07R3TWDTM` | Amazon Brand - Movian Keitele - 2 Seater Sofa, 130 x 82 x 84, Light Grey | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 4/4 | 1.3 x 0.82 x 0.84 | x1 |
| sofa | generated | `gen_sofa_japandi_1_246e1bd6` | Generated japandi sofa (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 4/4 | 2.14 x 0.884 x 0.844 | x2.13275 |
| sofa | generated | `gen_sofa_japandi_2_98a7a89b` | Generated japandi sofa (2) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/5 | 2.11 x 0.897 x 0.915 | x2.10248 |
| sofa | objaverse | `objaverse_104ac40ef3ad4dac8079a11548c470e7` | Sofa | hask191919 | CC-BY-4.0 | – | scandinavian, modern | -Y (high) | 5/5 | 3.04 x 1.07 x 1.12 | x1 |
| armchair | abo | `abo_B07124WN69` | Amazon Brand – Rivet Huxley Mid-Century Modern Accent Chair, 28.3"W, Marine Blue | Amazon.com | CC-BY-4.0 | – | scandinavian, modern | -Y (high) | 5/5 | 0.719 x 0.889 x 0.864 | x1 |
| armchair | abo | `abo_B0719WQGYJ` | Amazon Brand – Rivet Emerly Modern Living Room Chair, 41"W, Pewter | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 4/5 | 1.04 x 0.889 x 0.864 | x1 |
| armchair | abo | `abo_B071FMSYCH` | Amazon Brand – Rivet Farr Lotus Accent Chair, Felt Grey | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.859 x 1.01 x 0.855 | x1 |
| armchair | abo | `abo_B072PZ4LQ2` | Amazon Brand – Rivet Emerly Modern Living Room Chair, 41"W, Ecru | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 1.04 x 0.889 x 0.865 | x1 |
| armchair | abo | `abo_B073G7BVCT` | Amazon Brand – Stone & Beam Highland Modern Wingback Living Room Accent Chair, 31.9"W, Oatmeal | Amazon.com | CC-BY-4.0 | – | neutral | -Y (high) | 5/4 | 0.764 x 0.948 x 1.08 | x1 |
| armchair | abo | `abo_B0746KJVP2` | Amazon Brand – Rivet Charlotte Mid-Century Modern Upholstered Gold Accent Chair, 29"W, Natural | Amazon.com | CC-BY-4.0 | – | modern minimal, modern | -Y (high) | 5/5 | 0.805 x 0.813 x 0.966 | x1 |
| armchair | abo | `abo_B075NR8HWJ` | Amazon Brand Movian Dofsan Chair 100 x 93 x 86 cm Grey | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 4/4 | 1 x 0.93 x 0.86 | x1 |
| armchair | abo | `abo_B075X2WN36` | Amazon Brand – Rivet Curved Tufted Velvet Accent Chair, Marina Mid-Century, 28.7"W, Hunter Green | Amazon.com | CC-BY-4.0 | – | modern | -Y (high) | 5/5 | 0.851 x 0.776 x 0.885 | x1 |
| armchair | abo | `abo_B075X467QG` | Amazon Brand – Stone & Beam Hillsboro Modern Wingback Living Room Accent Chair With Nailhead Trim, 29"W, Beige | Amazon.com | CC-BY-4.0 | – | classic | -Y (high) | 5/5 | 0.737 x 0.94 x 1.03 | x1 |
| armchair | abo | `abo_B075X4N3GM` | Amazon Brand – Rivet Aiden Tufted Mid-Century Modern Velvet Accent Chair, 35.4"W, Otter Grey | Amazon.com | CC-BY-4.0 | – | modern, neutral | -Y (high) | 5/5 | 0.928 x 0.843 x 0.773 | x1 |
| armchair | abo | `abo_B075X4N3J5` | Amazon Brand – Rivet Villain Mid-Century Modern Leather Metal Leg Accent Lounge Chair, 37.4"W, Black | Amazon.com | CC-BY-4.0 | – | modern minimal, modern | -Y (high) | 5/5 | 0.836 x 0.826 x 0.922 | x1 |
| armchair | abo | `abo_B07B4MSP7T` | Amazon Brand – Stone & Beam Aubree Farmhouse Accent Arm Chair, 32"W, Striped Red Linen | Amazon.com | CC-BY-4.0 | – | classic | -Y (high) | 4/5 | 0.933 x 1.06 x 1.12 | x1 |
| armchair | abo | `abo_B07DBDQJRF` | Amazon Brand – Ravenna Home Hughes Curved Back Tufted Patterned Accent Chair, 25"W, Arrow | Amazon.com | CC-BY-4.0 | – | classic | -Y (high) | 5/5 | 0.686 x 0.613 x 0.859 | x1 |
| armchair | abo | `abo_B07HZ9K9PG` | Amazon Brand – Stone & Beam Calhoun Living Room Accent Chair, 42"W, Ecru | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 5/4 | 1.18 x 1.01 x 1.02 | x1 |
| armchair | objaverse | `objaverse_124297e7e4574c48b9c1b814b6ddf516` | animated_sphere | ferhatsen | CC-BY-4.0 | – | classic | -Y (high) | 5/5 | 0.751 x 0.84 x 0.91 | x1 |
| armchair | objaverse | `objaverse_5b9e8ba19b1b454f82898ac4809f02b2` | Lpuvw | juliaowoc | CC-BY-4.0 | – | classic | -Y (high) | 5/5 | 0.533 x 0.612 x 0.613 | x0.0254 |
| armchair | objaverse | `objaverse_69f1c0489a144f3c98e66dcfe72b3969` | Oldfashioned armchair | yezzyx | CC-BY-4.0 | – | classic | -Y (high) | 5/5 | 0.533 x 0.612 x 0.613 | x0.0254 |
| armchair | objaverse | `objaverse_a07501cd7f6c40fc9cf4cf438e41bac1` | Chair_2 out of 12 | 3Dtrickster | CC-BY-4.0 | – | classic | -Y (high) | 5/5 | 0.832 x 0.857 x 1.23 | x0.01 |
| armchair | objaverse | `objaverse_b23ec9725c48494788d1d88104acbb4a` | High back Arm chair (Free Download) | dopaminecat | CC-BY-4.0 | – | scandinavian, modern | -Y (high) | 4/5 | 0.81 x 0.892 x 0.923 | x0.362583 |
| armchair | objaverse | `objaverse_da6d646358d1451fa751f1a9141290a3` | LPUVW | HannaPachurka | CC-BY-4.0 | – | classic | -Y (high) | 5/5 | 0.533 x 0.612 x 0.613 | x0.0254 |
| table_dining | abo | `abo_B075YMXWZC` | Amazon Brand – Rivet Mid-Century Modern Oak Dining Table, 63"L, Walnut Finish | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (low) | 5/4 | 1.61 x 0.811 x 0.755 | x1 |
| table_dining | abo | `abo_B075YPTG8S` | Amazon Brand – Rivet Industrial Mid-Century Modern Hairpin Dining Table, 70.9"L, Walnut and Black | Amazon.com | CC-BY-4.0 | – | modern minimal, modern, industrial | -Y (low) | 5/4 | 1.79 x 0.883 x 0.753 | x1 |
| table_dining | abo | `abo_B075Z9QB7N` | Amazon Brand – Rivet Industrial Wood and Metal Round Dining Kitchen Table, 35.4"W, Recycled Elm | Amazon.com | CC-BY-4.0 | – | industrial | -Y (low) | 5/5 | 0.885 x 0.885 x 0.658 | x1 |
| table_dining | abo | `abo_B076NNYB3P` | Amazon Brand – Stone & Beam Dunbar Wood Dining Room Kitchen Table, 78"L, Oak Finish | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (low) | 4/4 | 1.98 x 1.02 x 0.762 | x1 |
| table_dining | abo | `abo_B07B7BGXN9` | Amazon Brand – Stone & Beam Alejandra Casual Wood Dining Kitchen Table, 78"-98"L, Brown | Amazon.com | CC-BY-4.0 | – | rustic | -Y (low) | 4/5 | 1.97 x 1.07 x 0.793 | x1 |
| table_dining | abo | `abo_B07B82PXCM` | Amazon Brand – Stone & Beam Bradhurst Casual Farmhouse Wood Dining Kitchen Table, 61"-84"L, White | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern, rustic | -Y (low) | 5/4 | 1.5 x 0.922 x 0.743 | x1 |
| table_dining | abo | `abo_B07B82PXD8` | Amazon Brand – Rivet Ian Modern Medium Dining Kitchen Table, Expandable, 60-80"L, Brown | Amazon.com | CC-BY-4.0 | – | scandinavian, minimal, modern | -Y (low) | 5/5 | 1.4 x 0.757 x 0.76 | x1 |
| table_dining | abo | `abo_B07B82WF6G` | Amazon Brand – Rivet Mid-Century Modern Wood Round Dining Kitchen Table, 43.3"W, Beige | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (low) | 5/5 | 1.04 x 1.04 x 0.666 | x1 |
| table_dining | abo | `abo_B07H8SZNZF` | Movian Moselle Dining Table, 160 x 76 x 90cm, Oak Sonoma Colour | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (low) | 4/4 | 1.6 x 0.9 x 0.76 | x1 |
| table_dining | abo | `abo_B07H93GTHW` | Amazon Brand - Movian Kuban Dining Table, 160 x 78 x 90cm, Brown Oak-Effect Table Top/Black Legs | Amazon.com | CC-BY-4.0 | – | modern minimal, industrial | -Y (low) | 5/5 | 1.58 x 0.881 x 0.736 | x1 |
| table_dining | abo | `abo_B07K7K25NM` | Amazon Brand - Alkove Hayes Solid Wood Dining Table with Stainless Steel Base, Seats 6, 180 x 90 x 75cm, Wild Oak/Stainless Steel | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (low) | 5/5 | 1.8 x 0.9 x 0.75 | x1 |
| table_dining | abo | `abo_B07M6PKC6B` | Amazon Brand – Ravenna Home Traditional Dining Table 29"H, Gray and Rustic Honey Pine | Amazon.com | CC-BY-4.0 | – | scandinavian, minimal, modern | -Y (low) | 4/4 | 0.747 x 0.747 x 0.738 | x1 |
| table_dining | abo | `abo_B07ML7P94G` | Amazon Brand – Ravenna Home Traditional Dining Table 29"H, Black and Rustic Honey Pine | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, minimal, modern, rustic | -Y (low) | 4/4 | 0.747 x 0.747 x 0.738 | x1 |
| table_dining | abo | `abo_B07QGWMTDY` | Amazon Brand – Rivet Fulton Modern Rustic Dining Table, 71"L, Natural | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (low) | 5/4 | 1.8 x 0.991 x 0.762 | x1 |
| table_dining | abo | `abo_B07RT5JN33` | Amazon Brand Movian Kyyvesi Dining Table 120.5 x 71.4 x 76 cm Walnut Effect | Amazon.com | CC-BY-4.0 | – | modern minimal, industrial | -Y (low) | 5/5 | 1.21 x 0.714 x 0.76 | x1 |
| table_dining | abo | `abo_B07SJ75Y1M` | Amazon Brand - Alkove Hayes Classic Fixed Solid Wood Dining Table, Seats 4-6, 130 x 90 x 75cm, Wild Oak | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (low) | 5/4 | 1.3 x 0.9 x 0.75 | x1 |
| table_dining | abo | `abo_B07VDD563W` | Amazon Brand - Movian Kyyvesi, Dining Table, 180 x 90 x 75 cm, Oak Effect | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (low) | 4/4 | 1.8 x 0.9 x 0.757 | x1 |
| table_dining | abo | `abo_B0853Q71J6` | Amazon Brand – Rivet Mid-Century Modern Pine Extendable Dining Table, 39"–77"W, Brown | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (low) | 5/5 | 0.991 x 0.991 x 0.754 | x1 |
| table_dining | objaverse | `objaverse_3b4ee19c627e4fb4a3305621cf925aa2` | Dining Set | dan2211082 | CC-BY-4.0 | – | rustic, neutral | -Y (low) | 4/5 | 1.31 x 1.23 x 0.704 | x0.0077457 |
| table_dining | objaverse | `objaverse_724d93a7f3644f96909e8c55909c6418` | A table, chairs & few cups | Sahramin | CC-BY-4.0 | – | scandinavian, rustic | -Y (low) | 4/4 | 1.17 x 1.2 x 0.85 | x0.601997 |
| table_coffee | abo | `abo_B01LWVEZ1C` | Amazon Brand - Alkove Waverly Large Coffee Table with Shelf in Light Oak Finish | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (low) | 4/5 | 0.899 x 0.45 x 0.452 | x1 |
| table_coffee | abo | `abo_B072ZK2FZ6` | Amazon Brand – Rivet Industrial Modern Wood and Metal Coffee Table, 31.5"W, Walnut | Amazon.com | CC-BY-4.0 | – | japandi, modern minimal, minimal, modern | -Y (low) | 5/5 | 0.804 x 0.361 x 0.576 | x1 |
| table_coffee | abo | `abo_B072ZK885D` | Amazon Brand – Rivet Allyson Mid-Century Modern Two-Shelf Adjustable Coffee Table, Walnut | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (low) | 5/5 | 1.08 x 0.527 x 0.429 | x1 |
| table_coffee | abo | `abo_B074KLRCPW` | Amazon Brand – Rivet Modern Round Glass and Gold Coffee Table, 36"W, Gold Finish | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (low) | 5/4 | 0.914 x 0.914 x 0.47 | x1 |
| table_coffee | abo | `abo_B075Z8WD59` | Amazon Brand – Rivet Hillside Antiqued Round Coffee Table, 39.4"D, Wood and Bronze | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, neutral | -Y (low) | 4/5 | 1 x 1 x 0.409 | x1 |
| table_coffee | abo | `abo_B075ZBVZPB` | Amazon Brand – Stone & Beam Larson Industrial Wood & Metal Coffee Table, 50"W, Walnut | Amazon.com | CC-BY-4.0 | – | industrial | -Y (low) | 5/5 | 0.99 x 0.452 x 0.399 | x1 |
| table_coffee | abo | `abo_B07DBFQV23` | Amazon Brand – Ravenna Home Parker Coffee Table, 47.2"W, Marble &amp; Gold | Amazon.com | CC-BY-4.0 | – | modern minimal, modern | -Y (low) | 5/5 | 1.2 x 0.577 x 0.405 | x1 |
| table_coffee | abo | `abo_B07GDMBZJJ` | Amazon Brand - Rivet Leaf-Shaped Coffee Table, 120 x 60 x 36cm, MDF with Walnut Veneer/Black Metal Base | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (low) | 5/5 | 1.2 x 0.598 x 0.36 | x1 |
| table_coffee | abo | `abo_B07GDSF3MR` | Amazon Brand - Rivet Round Coffee Table with Solid Wood Legs, 80 x 80 x 36cm, MDF with Walnut Veneer/Solid Beech Wood | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (low) | 5/5 | 0.8 x 0.8 x 0.36 | x1 |
| table_coffee | abo | `abo_B07GDYVV9M` | Amazon Brand - Rivet Triangular Coffee Table with Solid Wood Legs, 105 x 60 x 37cm, MDF with Walnut Veneer/Solid Beech Wood | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (low) | 5/5 | 1.01 x 0.601 x 0.365 | x1 |
| table_coffee | abo | `abo_B07L85XV75` | ROCKPOINT Argus Lift-Top Wood Coffee Table, Sandy Oak | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (low) | 5/5 | 1.09 x 0.493 x 0.48 | x1 |
| table_coffee | abo | `abo_B07L8DT2XT` | Phoenix Home Rustic Industrial Solid Wood and Steel Open Shelf Coffee Table, Brown | Amazon.com | CC-BY-4.0 | – | japandi, modern minimal, minimal, modern, industrial | -Y (low) | 5/4 | 1.07 x 0.61 x 0.457 | x1 |
| table_coffee | abo | `abo_B07QF9Y71V` | Amazon Brand – Stone & Beam Industrial Coffee Table, 53"W, Antique Natural and Black | Amazon.com | CC-BY-4.0 | – | modern minimal, industrial | -Y (low) | 5/4 | 1.35 x 0.75 x 0.4 | x1 |
| table_coffee | abo | `abo_B07QFB1TLZ` | Amazon Brand – Stone & Beam Ryder Industrial Round Coffee Table, 43.3" Diameter, Brushed Natural Antique Copper | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (low) | 5/4 | 1.1 x 1.1 x 0.42 | x1 |
| table_coffee | abo | `abo_B07SQ9P548` | Amazon Brand - Solimo Veronica Engineered Wood Coffee Table (Espresso Finish) | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal | -Y (low) | 5/4 | 1.05 x 0.59 x 0.46 | x1 |
| table_coffee | objaverse | `objaverse_01ff88bfc0034211b9f4996d620bc333` | Palette Table | Javier.Cantero | CC-BY-4.0 | – | japandi, modern minimal, minimal, modern, industrial, rustic | -Y (low) | 4/4 | 1.29 x 0.861 x 0.25 | x10.5567 |
| table_coffee | objaverse | `objaverse_956a47ccc1a54a40a8711f3852d54433` | 55555 | Gulin | CC-BY-4.0 | – | modern minimal, modern | -Y (low) | 5/5 | 1 x 0.6 x 0.395 | x0.001 |
| table_coffee | objaverse | `objaverse_bbe1d47c0d714884a66c53d6c1e5d177` | MESA COMEDOR | Fer.Arq | CC-BY-4.0 | – | japandi, modern minimal, minimal, modern | -Y (low) | 5/5 | 0.894 x 0.894 x 0.517 | x0.541335 |
| table_coffee | objaverse | `objaverse_c17577daa87849d09960669606c0ce27` | Modern Table | Athlas | CC-BY-4.0 | – | japandi, modern minimal, minimal, modern | -Y (low) | 5/4 | 1.31 x 0.59 x 0.6 | x0.655745 |
| table_coffee | objaverse | `objaverse_f4031bb5f7e64ebca4c37d4fa5ba6e8d` | LP Table | doplerato | CC-BY-4.0 | – | classic, rustic | -Y (low) | 4/4 | 1.2 x 0.669 x 0.36 | x8.32595 |
| desk | abo | `abo_B01FK3FWNG` | Amazon Brand - Movian Haven Retro Desk with Riser, Grey Oak, 113.54 x 60.45 x 89.92 cm | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, modern | -Y (high) | 5/4 | 1.14 x 0.605 x 0.899 | x1 |
| desk | abo | `abo_B01MXKMRK4` | Marchio Amazon - Movian Scrivania Candon, Marrone medio, 114,3 x 49,53 x 76,454 cm | Amazon.com | CC-BY-4.0 | – | modern minimal, industrial | -Y (high) | 5/4 | 1.13 x 0.511 x 0.752 | x1 |
| desk | abo | `abo_B075ZBVZST` | Amazon Brand – Rivet Mid-Century Curved Wood Table Home Office Computer Desk, 48.4"L, Walnut | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, modern | -Y (high) | 5/5 | 1.26 x 0.486 x 0.8 | x1 |
| desk | abo | `abo_B07B7DFS3S` | Amazon Brand – Stone & Beam Industrial Metal Office Computer Desk, 60"W, Power Sit to Standing Table, Brown/Black | Amazon.com | CC-BY-4.0 | – | industrial, rustic | -Y (high) | 5/4 | 1.54 x 0.784 x 0.725 | x1 |
| desk | abo | `abo_B07B7DKRW4` | Amazon Brand – Stone & Beam Anne Farmhouse French Wood Desk, 62"W, Blue | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 1.29 x 0.63 x 0.861 | x1 |
| desk | abo | `abo_B07GF5DCK2` | Amazon Brand - Rivet Mid-Century Home Office Computer Desk with 1 Drawer & Curved Corners, 57 x 123 x 79cm, White/MDF with Walnut Veneer | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, modern | -Y (high) | 4/4 | 1.21 x 0.534 x 0.807 | x1 |
| desk | abo | `abo_B07GFL6RF5` | Amazon Brand - Movian Idro 3-Drawer Desk, 56 x 110 x 73.5cm, Light Brown/Oak Foil Finish | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 4/4 | 1.1 x 0.56 x 0.735 | x1 |
| desk | abo | `abo_B07GFS1V51` | Amazon Brand - Movian Idro 4-Drawer Desk, 56 x 110 x 73cm, Light Brown/Oak Foil Finish | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 4/4 | 1.1 x 0.56 x 0.73 | x1 |
| desk | abo | `abo_B07GFT639N` | Amazon Brand - Movian Indre 1-Drawer Desk, 56 x 110 x 73cm, Light Brown/Oak Foil Finish | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 5/4 | 1.1 x 0.56 x 0.73 | x1 |
| desk | abo | `abo_B07HSCRFTN` | Amazon Brand – Rivet Mid-Century Desk - 35 Inch, Natural | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/5 | 1.19 x 0.769 x 1.06 | x1 |
| desk | abo | `abo_B07JXXR83F` | Amazon Brand - Movian Stanberg 1-Door 1-Drawer Writing Desk, 140 x 55 x 76cm, Light Brown Oak-Effect/Black | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, modern | -Y (high) | 5/4 | 1.4 x 0.55 x 0.76 | x1 |
| desk | abo | `abo_B07PVL2N3D` | AmazonBasics Classic, Home Office Computer Desk With Shelves, Black | Amazon.com | CC-BY-4.0 | – | modern minimal, industrial | -Y (high) | 4/4 | 0.902 x 0.498 x 0.749 | x1 |
| desk | abo | `abo_B07PYYRV2L` | AmazonBasics Foldable Standing Computer Desk with Storage Shelf, Adjustable Height, Easy Assembly - Black | Amazon.com | CC-BY-4.0 | – | modern minimal, industrial | -Y (high) | 4/4 | 0.922 x 0.52 x 0.85 | x1 |
| desk | abo | `abo_B07QV37J6B` | AmazonBasics Gaming Computer Desk with Storage for Controller, Headphone & Speaker - Red | Amazon.com | CC-BY-4.0 | – | modern minimal, industrial | -Y (high) | 4/4 | 1.28 x 0.588 x 0.913 | x1 |
| desk | abo | `abo_B07RVBPWG9` | Amazon Brand-Movian Ljungan Desk, 114 x 60 x 90cm, Dark Brown/Black | Amazon.com | CC-BY-4.0 | – | modern minimal, industrial | -Y (high) | 5/4 | 1.14 x 0.936 x 0.998 | x1 |
| desk | abo | `abo_B07TKY3L6X` | Amazon Brand - Movian Côa 4-Drawer Desk, 160 x 73 x 77.5cm, Vintage Dark Brown Oak-Effect/Black Metal | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern, industrial | -Y (high) | 5/5 | 1.6 x 0.73 x 0.78 | x1 |
| desk | abo | `abo_B082DFL4JW` | Amazon Brand – Rivet Avery Industrial Home Office Writing Desk with Metal Base, 40"W, Chestnut Brown Finish | Amazon.com | CC-BY-4.0 | – | japandi, modern minimal, industrial | -Y (high) | 5/4 | 1.02 x 0.47 x 0.762 | x1 |
| desk | abo | `abo_B0876NZQ9C` | AmazonBasics 40" Multipurpose Foldable Computer Study Desk - Natural | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 5/4 | 1.02 x 0.508 x 0.762 | x1 |
| desk | objaverse | `objaverse_1b256f6ce7924f59a756fe8f7ba69416` | FF Desk Drawer 3D Test 5 Obj | fabcreative | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/4 | 1.34 x 0.923 x 0.65 | x0.000311303 |
| desk | objaverse | `objaverse_b05862a2023f4c02988b3bb3004f6ff6` | Table Colored DZ | slayer11 | CC-BY-4.0 | – | modern minimal, minimal, modern | +Y (high) | 4/5 | 1.1 x 0.647 x 0.807 | x0.0254 |
| chair | abo | `abo_B01MQJV7ID` | AmazonBasics Sedia direzionale da ufficio con schienale alto, regolabile in altezza - Marrone | Amazon.com | CC-BY-4.0 | – | modern | -Y (high) | 5/5 | 0.662 x 0.739 x 1.11 | x1 |
| chair | abo | `abo_B0728NW8FP` | Amazon Brand – Rivet Ashworth Armless Velvet Accent Chair, 21.6"W, Navy | Amazon.com | CC-BY-4.0 | – | modern minimal, modern | -Y (high) | 5/5 | 0.521 x 0.55 x 0.805 | x1 |
| chair | abo | `abo_B07C9W437G` | Amazon Brand – Rivet Federal Mid-Century Modern Wood Dining Room Kitchen Chairs, 36 Inch Height, Set of 2, Black | Amazon.com | CC-BY-4.0 | – | modern minimal, modern | -Y (high) | 5/4 | 0.504 x 0.567 x 0.82 | x1 |
| chair | abo | `abo_B07DBD9WHX` | Amazon Brand – Ravenna Home Armless Tufted Turned Wood Leg Accent Chair, 29"W, Blue | Amazon.com | CC-BY-4.0 | – | classic | -Y (high) | 5/5 | 0.74 x 0.719 x 0.77 | x1 |
| chair | abo | `abo_B07DBHCKHY` | Amazon Brand – Ravenna Home Tufted Armless English Roll Traditional Accent Chair, 26.8"W, Merlot Red | Amazon.com | CC-BY-4.0 | – | classic | -Y (high) | 5/5 | 0.582 x 0.605 x 0.75 | x1 |
| chair | abo | `abo_B07FY8PZBH` | Phoenix Home PU Leather Dining Chair Set of 2, 18.11" Length x 21.65" Width x 30.7" Height, Brown | Amazon.com | CC-BY-4.0 | – | industrial | -Y (high) | 5/5 | 0.46 x 0.551 x 0.78 | x1 |
| chair | abo | `abo_B07JK8CL2Z` | Amazon Brand - Movian Square | Amazon.com | CC-BY-4.0 | – | scandinavian, modern | -Y (high) | 5/4 | 0.57 x 0.57 x 0.78 | x1 |
| chair | abo | `abo_B07K7K7GKC` | Amazon Brand - Alkove - Hayes - Modern Solid Wood Chairs Set of 2 with Padded Seat - Wild Oak | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/4 | 0.457 x 0.561 x 0.955 | x1 |
| chair | abo | `abo_B07QJ24FSL` | Amazon Brand – Ravenna Home Dining Chairs, Set of 2, 40"H, Praline | Amazon.com | CC-BY-4.0 | – | classic | -Y (high) | 5/5 | 0.513 x 0.66 x 1.02 | x1 |
| chair | abo | `abo_B084RZVHD2` | Amazon Brand – Rivet Erikson Vegan Leather Woven Dining Chair, Set of 2, 18"W, Beige | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/4 | 0.473 x 0.533 x 0.905 | x1 |
| chair | abo | `abo_B084W2GNQW` | Amazon Brand – Stone & Beam Vivianne Modern Upholstered Armless Dining Chair with Casters, 19.7"W, Slate | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 4/5 | 0.503 x 0.699 x 0.927 | x1 |
| chair | abo | `abo_B0857JLP6K` | Amazon Brand – Stone & Beam Modern Farmhouse Birch Dining Chair, 17.5"W, Dark Gray | Amazon.com | CC-BY-4.0 | – | minimal, industrial | -Y (high) | 4/5 | 0.45 x 0.546 x 0.991 | x1 |
| chair | abo | `abo_B0857JM2NC` | Amazon Brand – Stone & Beam Mid-Century Beech and Rattan Dining Chair with Arms, 21.9"W, Natural | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/4 | 0.556 x 0.495 x 0.762 | x1 |
| chair | objaverse | `objaverse_039c6026571943d6ac45c6816bcc7ff1` | Rocking Chair | Christian | CC-BY-4.0 | – | classic | -Y (high) | 5/5 | 0.41 x 0.609 x 0.822 | x0.657204 |
| chair | objaverse | `objaverse_0723b35415b0462eb5c01140b6b70340` | Old chair | Dani Ortega | CC-BY-4.0 | – | classic | -Y (high) | 5/5 | 0.522 x 0.552 x 0.7 | x0.640063 |
| chair | objaverse | `objaverse_1625701880c54b7d9f50e77455cef39b` | Wicker Chair | Scott Thorne | CC-BY-4.0 | – | mediterranean | -X (high) | 4/4 | 0.577 x 0.566 x 0.957 | x1 |
| chair | objaverse | `objaverse_47a690dcecf847fca99c4f89111db85b` | Char 2 | DimaSP | CC-BY-4.0 | – | classic, rustic | -Y (high) | 4/5 | 0.462 x 0.541 x 1.01 | x0.808639 |
| chair | objaverse | `objaverse_acf6497a3d274d90ad3750510348f07a` | chare | DimaSP | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern, rustic | -Y (high) | 5/5 | 0.455 x 0.525 x 0.999 | x1 |
| chair | objaverse | `objaverse_cb43e2abac66494d81e1e7116eb47043` | Vintage Chair | Maycho | CC-BY-4.0 | – | industrial, rustic | -Y (high) | 4/4 | 0.483 x 0.604 x 1.03 | x1 |
| chair | objaverse | `objaverse_d2785b57e7da45858f2fe8bf4dedd68d` | Chair | 杭州维界科技有限公司 | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/5 | 0.517 x 0.503 x 0.829 | x0.01 |
| wardrobe | abo | `abo_B07B3XXD3P` | Vida Designs Corona Wardrobe, 3 Door, Solid Pine Wood, Solid Pine Wood, Distressed Waxed Pine Bedroom Wooden Storage Mexican Furniture | Amazon.com | CC-BY-4.0 | – | scandinavian, rustic, neutral | -Y (high) | 4/4 | 1.5 x 0.57 x 1.87 | x1 |
| wardrobe | abo | `abo_B07GFRKNR1` | Amazon Brand - Movian Inari Modern 2-Door 2-Drawer Wardrobe, 100 x 57 x 180 cm, Light Brown Oak-Effect | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 5/4 | 0.991 x 0.577 x 1.81 | x1 |
| wardrobe | abo | `abo_B07GFS1R5B` | Amazon Brand - Movian Indre 3-Door 3-Drawer Wardrobe, 129 x 51 x 191cm, Dark Grey | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 1.29 x 0.51 x 1.91 | x1 |
| wardrobe | abo | `abo_B07GFS1VB6` | Amazon Brand - Movian Kolva Sliding 2-Door Wardrobe, 180 x 61 x 197cm, Light Brown Oak-Effect | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 5/5 | 1.78 x 0.629 x 1.96 | x1 |
| wardrobe | abo | `abo_B07GFS1WDY` | Amazon Brand - Movian Inari Modern 2-Door 2-Drawer Wardrobe, 100 x 57 x 180 cm, Dark Grey | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal | -Y (high) | 5/4 | 0.991 x 0.577 x 1.81 | x1 |
| wardrobe | abo | `abo_B07GFWW3S8` | Amazon Brand - Movian Kolva Sliding 2-Door Wardrobe, 180 x 61 x 197cm, Dark Grey | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal | -Y (high) | 4/4 | 1.78 x 0.629 x 1.96 | x1 |
| wardrobe | abo | `abo_B07H8JN9QF` | Amazon Brand - Movian Morava 4-Door 2-Drawer Wardrobe with Mirrors, 200 x 59 x 212cm, Light Brown Oak-Effect | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 4/4 | 2 x 0.598 x 2.16 | x1 |
| wardrobe | abo | `abo_B07H8PS4FZ` | Amazon Brand - Movian Cinca 5-Door Wardrobe with Mirrors and Internal Storage Compartments, 226 x 216 x 62cm, White/Oak-Colour Accents | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 4/4 | 2.16 x 0.59 x 2.26 | x1 |
| wardrobe | abo | `abo_B07H8V7P3H` | Amazon Brand - Movian Moselle 2-Door Wardrobe, 100 x 60 x 196 cm, Light Brown Oak-Effect/White | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 4/4 | 1 x 0.6 x 1.96 | x1 |
| wardrobe | abo | `abo_B07JGPKZYT` | Amazon Brand - Movian Mira 4-Door Wardrobe with Mirrors, 181 x 207 x 58cm, Light Brown Oak-Effect | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 5/4 | 1.81 x 0.58 x 2.07 | x1 |
| wardrobe | generated | `gen_wardrobe_classic_1_2bc1a548` | Generated classic wardrobe (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | classic | -Y (high) | 5/4 | 1.44 x 0.79 x 2.45 | x2.4431 |
| wardrobe | generated | `gen_wardrobe_industrial_1_79cac0b4` | Generated industrial wardrobe (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | industrial | -Y (high) | 5/4 | 1.36 x 0.798 x 2.6 | x2.5954 |
| wardrobe | generated | `gen_wardrobe_rustic_1_97c119f6` | Generated rustic wardrobe (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | scandinavian, rustic, neutral | -Y (high) | 5/5 | 1.25 x 0.805 x 2.43 | x2.42303 |
| wardrobe | generated | `gen_wardrobe_scandinavian_1_d0aa2dad` | Generated scandinavian wardrobe (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 5/4 | 1.42 x 0.801 x 2.59 | x2.58499 |
| wardrobe | objaverse | `objaverse_05a035c3347645b8a7ceb6d65f825ac3` | Dikkies Closet | klaxoneer | CC-BY-4.0 | – | classic | -Y (high) | 5/4 | 1.14 x 0.624 x 1.76 | x1 |
| wardrobe | objaverse | `objaverse_08a3baeb2e0847939d53027824de5a49` | Wardrobe | Kevin98 | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | +X (high) | 4/4 | 1.66 x 0.688 x 2.11 | x0.20234 |
| wardrobe | objaverse | `objaverse_094697a23146463cb5564ac8bf89e5c4` | Traditional Mennonite corner cabinet | vinigor | CC-BY-NC-4.0 | non_commercial | classic | -Y (high) | 4/4 | 1.45 x 0.786 x 2.6 | x0.000995894 |
| wardrobe | objaverse | `objaverse_6d443f619ecd404a81769c70f447ba86` | Cabinet | trijoko.maryadi | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 4/4 | 1.35 x 0.731 x 2.6 | x2.22526 |
| wardrobe | objaverse | `objaverse_b3a99e956be64ab6958f7f5e1895f031` | Warn Wardrobe | seenoise | CC-BY-4.0 | – | classic, rustic | -Y (high) | 4/4 | 1.29 x 0.564 x 2.31 | x1 |
| wardrobe | objaverse | `objaverse_b46803ba0bc64e12b31f832fb761c4e0` | Simple Tall Shelf | Blender3D | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 4/4 | 1.05 x 0.563 x 2.6 | x0.118158 |
| fridge | generated | `gen_fridge_industrial_1_03996e16` | Generated industrial fridge (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, industrial | -Y (high) | 4/4 | 0.637 x 0.795 x 1.41 | x1.40306 |
| fridge | generated | `gen_fridge_japandi_1_4c9cd582` | Generated japandi fridge (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.749 x 0.676 x 1.68 | x1.67827 |
| fridge | generated | `gen_fridge_japandi_2_4c7dbc82` | Generated japandi fridge (2) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, modern | -Y (high) | 4/4 | 0.682 x 0.742 x 1.51 | x1.51094 |
| fridge | generated | `gen_fridge_japandi_3_38a9d0f8` | Generated japandi fridge (3) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.732 x 0.691 x 1.49 | x1.48328 |
| fridge | generated | `gen_fridge_mediterranean_1_1460e264` | Generated mediterranean fridge (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.653 x 0.775 x 1.48 | x1.47878 |
| fridge | generated | `gen_fridge_modern_minimal_1_c27ed7d7` | Generated modern minimal fridge (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.656 x 0.772 x 1.67 | x1.67019 |
| fridge | generated | `gen_fridge_rustic_1_06be6df4` | Generated rustic fridge (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | classic | -Y (high) | 4/4 | 0.631 x 0.802 x 1.37 | x1.3639 |
| fridge | generated | `gen_fridge_scandinavian_1_315b4d87` | Generated scandinavian fridge (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.626 x 0.809 x 1.37 | x1.36995 |
| fridge | objaverse | `objaverse_2071bda681b642218b6829b82e4fd93b` | Refrigerator - Grey Polished Metal | Glowbox 3D | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.766 x 0.661 x 1.54 | x0.193519 |
| fridge | objaverse | `objaverse_66878d980a364b2db1a5cc44c67bb45d` | Fridge | Yaseen Ali | CC-BY-4.0 | – | modern minimal, modern | -Y (high) | 4/4 | 0.726 x 0.499 x 1.33 | x0.0254 |
| fridge | objaverse | `objaverse_68d69bbf7a454a09a2536ac0762532f3` | Old Fridge | golddog | CC-BY-4.0 | – | modern minimal, minimal, modern | +X (high) | 4/4 | 0.725 x 0.698 x 1.09 | x0.419674 |
| fridge | objaverse | `objaverse_c9c4e705bf794cb88d5d8726095f4917` | Haier Refrigerator | cgwings | CC-BY-NC-4.0 | non_commercial | modern minimal, modern | +Y (high) | 4/4 | 0.833 x 0.918 x 1.8 | x1 |
| fridge | objaverse | `objaverse_f32ec9229a8749d1b79245813fbd6c31` | Stylized Fridge | sauti | CC-BY-4.0 | – | modern minimal, minimal, modern | +X (high) | 4/4 | 0.745 x 0.679 x 1.53 | x0.347346 |
| stove | generated | `gen_stove_classic_1_4cdc3ba9` | Generated classic stove (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | classic | -Y (high) | 5/4 | 1 x 0.629 x 0.859 | x1 |
| stove | generated | `gen_stove_industrial_1_59fd0342` | Generated industrial stove (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern, industrial | -Y (high) | 5/4 | 1 x 0.686 x 0.879 | x1 |
| stove | generated | `gen_stove_japandi_1_2c35be6c` | Generated japandi stove (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 4/4 | 0.872 x 0.73 x 0.8 | x0.870564 |
| stove | generated | `gen_stove_modern_1_d7aca74d` | Generated modern stove (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 1 x 0.643 x 0.83 | x1 |
| stove | generated | `gen_stove_modern_minimal_1_18c4c83a` | Generated modern minimal stove (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.938 x 0.771 x 0.8 | x0.935904 |
| stove | generated | `gen_stove_rustic_1_f05488ba` | Generated rustic stove (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | classic | -Y (high) | 5/4 | 1 x 0.679 x 0.845 | x1 |
| stove | generated | `gen_stove_scandinavian_1_acd46212` | Generated scandinavian stove (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern | -Y (high) | 5/4 | 0.897 x 0.724 x 0.8 | x0.895985 |
| stove | generated | `gen_stove_scandinavian_2_4aebb9bc` | Generated scandinavian stove (2) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 5/4 | 1 x 0.8 x 0.8 | x1.00038 |
| stove | objaverse | `objaverse_68e164f1a9414c29820ac2eaf6d8ac04` | Stove from Poly by Google | IronEqual | CC-BY-4.0 | – | modern minimal, modern | -Y (high) | 4/4 | 0.67 x 0.6 x 0.819 | x0.0254 |
| stove | objaverse | `objaverse_7c5c9dec5c2e4ff998c386410b0e3686` | Stove | Daniyal Malik | CC-BY-4.0 | – | industrial | -X (high) | 4/4 | 0.592 x 0.71 x 0.867 | x0.00228858 |
| stove | objaverse | `objaverse_934716ccd00d4f6ba9555d1cea788488` | R RETRO FIRIN | Motto Teknoloji | CC-BY-4.0 | – | modern | -Y (high) | 4/4 | 0.51 x 0.547 x 1.2 | x0.854944 |
| sink_kitchen | generated | `gen_sink_kitchen_japandi_1_a61d924d` | Generated japandi sink kitchen (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 5/4 | 1.06 x 0.494 x 0.8 | x1.05391 |
| sink_kitchen | generated | `gen_sink_kitchen_japandi_2_d6ae0419` | Generated japandi sink kitchen (2) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal | -Y (high) | 4/4 | 1 x 0.56 x 0.882 | x1 |
| sink_kitchen | generated | `gen_sink_kitchen_japandi_3_1462384d` | Generated japandi sink kitchen (3) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 1 x 0.567 x 0.895 | x1 |
| sink_kitchen | generated | `gen_sink_kitchen_japandi_4_329115ec` | Generated japandi sink kitchen (4) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 1 x 0.565 x 0.863 | x1 |
| sink_kitchen | generated | `gen_sink_kitchen_mediterranean_1_ae36322f` | Generated mediterranean sink kitchen (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | minimal, modern | -Y (high) | 4/4 | 0.811 x 0.675 x 1 | x1 |
| sink_kitchen | generated | `gen_sink_kitchen_modern_1_5b97156d` | Generated modern sink kitchen (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.928 x 0.611 x 1 | x1 |
| sink_kitchen | generated | `gen_sink_kitchen_modern_2_b348b4dc` | Generated modern sink kitchen (2) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 1 x 0.47 x 0.811 | x1 |
| sink_kitchen | generated | `gen_sink_kitchen_rustic_1_3b005a69` | Generated rustic sink kitchen (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, modern | -Y (high) | 5/4 | 0.689 x 0.545 x 1 | x1 |
| sink_kitchen | generated | `gen_sink_kitchen_scandinavian_1_dbad65c6` | Generated scandinavian sink kitchen (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 5/4 | 0.598 x 0.83 x 1 | x1 |
| sink_kitchen | generated | `gen_sink_kitchen_scandinavian_2_470fa047` | Generated scandinavian sink kitchen (2) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 5/4 | 0.859 x 0.598 x 1 | x1 |
| sink_kitchen | generated | `gen_sink_kitchen_scandinavian_3_3e309f4c` | Generated scandinavian sink kitchen (3) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.884 x 0.644 x 1 | x1 |
| washbasin | generated | `gen_washbasin_classic_1_9bd9b8cd` | Generated classic washbasin (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.606 x 0.509 x 0.623 | x0.623132 |
| washbasin | generated | `gen_washbasin_industrial_1_6794b9a5` | Generated industrial washbasin (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 5/4 | 0.847 x 0.646 x 1 | x1 |
| washbasin | generated | `gen_washbasin_japandi_1_299a0eb2` | Generated japandi washbasin (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 5/5 | 0.633 x 0.487 x 0.64 | x0.639279 |
| washbasin | generated | `gen_washbasin_japandi_2_6d594c3b` | Generated japandi washbasin (2) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 5/4 | 0.607 x 0.509 x 0.373 | x0.605959 |
| washbasin | generated | `gen_washbasin_japandi_3_fc4e0710` | Generated japandi washbasin (3) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 5/4 | 0.576 x 0.536 x 0.673 | x0.672191 |
| washbasin | generated | `gen_washbasin_mediterranean_1_93c90025` | Generated mediterranean washbasin (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 5/4 | 0.543 x 0.569 x 0.691 | x0.689927 |
| washbasin | generated | `gen_washbasin_minimal_1_9dc765fb` | Generated minimal washbasin (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.592 x 0.521 x 0.321 | x0.591307 |
| washbasin | generated | `gen_washbasin_modern_1_833baa60` | Generated modern washbasin (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.616 x 0.501 x 0.652 | x0.650885 |
| washbasin | generated | `gen_washbasin_modern_minimal_1_d5536003` | Generated modern minimal washbasin (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 5/4 | 0.64 x 0.483 x 0.636 | x0.638448 |
| washbasin | generated | `gen_washbasin_rustic_1_2d54af97` | Generated rustic washbasin (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/4 | 0.611 x 0.505 x 0.723 | x0.721793 |
| washbasin | generated | `gen_washbasin_scandinavian_1_6efd9d50` | Generated scandinavian washbasin (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 5/4 | 0.575 x 0.537 x 0.34 | x0.574398 |
| washbasin | objaverse | `objaverse_295384601e0d4f1985a919253330d59d` | Combo CEG-50BF | Stala | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.574 x 0.538 x 0.474 | x0.312352 |
| washbasin | objaverse | `objaverse_3eafb89804b54c8e8cbe35e4d456e0a9` | Bathroom | Thunder | CC-BY-SA-4.0 | share_alike | modern minimal, minimal, modern | +X (high) | 4/4 | 0.949 x 0.325 x 0.516 | x0.00323813 |
| washbasin | objaverse | `objaverse_493b70a6177d4a1385b6b0ce041a93b0` | same sink but less sanitary | GroundZer0 | CC-BY-4.0 | – | modern minimal, minimal | -Y (high) | 4/4 | 0.698 x 0.443 x 0.974 | x0.486948 |
| washbasin | objaverse | `objaverse_5248aa117842442980a2a2bbb5f3bfe6` | Mobilya1 | Emre.Topuz | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.873 x 0.354 x 0.991 | x0.00589654 |
| washbasin | objaverse | `objaverse_6458ac945c14458a8e5f4a470495f042` | Combo CEG40-50B | Stala | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.497 x 0.621 x 0.601 | x0.378707 |
| washbasin | objaverse | `objaverse_8580c4545d1649efb3503c6c2a012641` | Ingstav147 PULT ZRK V1 | KRONZI | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | +X (high) | 5/4 | 0.838 x 0.368 x 1.01 | x0.00698632 |
| washbasin | objaverse | `objaverse_ce1a06f7cbe1425099a145f851fc5dee` | Sink | Shining Salt | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.649 x 0.476 x 0.55 | x0.324323 |
| washbasin | objaverse | `objaverse_f76c502218884914a27148f656a9b656` | Bathroom1 | neutralize | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.663 x 0.501 x 0.598 | x0.0254 |
| toilet | generated | `gen_toilet_industrial_1_3cd5bde9` | Generated industrial toilet (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 5/4 | 0.53 x 0.865 x 1 | x1 |
| toilet | generated | `gen_toilet_japandi_1_42fdb46f` | Generated japandi toilet (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 5/5 | 0.415 x 0.692 x 0.724 | x0.722866 |
| toilet | generated | `gen_toilet_japandi_3_4e49add0` | Generated japandi toilet (3) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 5/4 | 0.405 x 0.709 x 0.717 | x0.716107 |
| toilet | generated | `gen_toilet_mediterranean_1_09b9f7e2` | Generated mediterranean toilet (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -X (high) | 5/4 | 0.756 x 0.38 x 0.807 | x0.805317 |
| toilet | generated | `gen_toilet_minimal_1_3799392b` | Generated minimal toilet (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.729 x 0.393 x 0.78 | x0.778891 |
| toilet | generated | `gen_toilet_rustic_1_c2ce66a1` | Generated rustic toilet (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 5/5 | 0.54 x 0.864 x 1 | x1 |
| toilet | generated | `gen_toilet_scandinavian_4_06dcb780` | Generated scandinavian toilet (4) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.527 x 0.865 x 1 | x1 |
| toilet | objaverse | `objaverse_0b3325fad3e740b1ac86173c90b56afd` | Toilettes | Lightningx | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.462 x 0.621 x 0.839 | x0.0146675 |
| toilet | objaverse | `objaverse_1bd73c9a74d14ce29e45c277570990e6` | Zenit Close Coupled Push Button Flush Toilet | Yaiyeondurising | CC-BY-SA-4.0 | share_alike | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.425 x 0.782 x 0.983 | x1 |
| toilet | objaverse | `objaverse_24d1b493899d407780140688abae19bc` | Toilet | Xill | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.453 x 0.633 x 0.801 | x0.744926 |
| toilet | objaverse | `objaverse_3446229dce1f47528fa871cc7669136c` | Toilet | Ali107_YT | CC-BY-4.0 | – | modern minimal, minimal, modern | +X (high) | 4/4 | 0.453 x 0.634 x 0.761 | x0.0015794 |
| toilet | objaverse | `objaverse_4398bcb5976945b08f195816340247b8` | Memoirs Stately Close Coupled Toilet | Yaiyeondurising | CC-BY-SA-4.0 | share_alike | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.479 x 0.791 x 0.783 | x1 |
| toilet | objaverse | `objaverse_5b18711616054a44b025d9272b745a6a` | Qualitas Bathrooms toilet low poly | Yaiyeondurising | CC-BY-4.0 | – | modern minimal, minimal, modern | +X (high) | 4/4 | 0.48 x 0.679 x 0.78 | x0.01 |
| toilet | objaverse | `objaverse_bd0f8d2bfba24376bec2b827a0cbbabe` | CWLCCST1-6DT01 Ld | trendforward | CC-BY-NC-4.0 | non_commercial | modern minimal, minimal, modern | +X (high) | 4/4 | 0.417 x 0.669 x 0.793 | x0.01 |
| toilet | objaverse | `objaverse_c901dfa120a0487a9f5c9a2d241f70ab` | Animated low poly toilet | Gamedirection | CC-BY-4.0 | – | modern minimal, minimal, modern | +X (high) | 4/4 | 0.406 x 0.706 x 0.831 | x0.00233133 |
| shower | generated | `gen_shower_industrial_1_d2ef1a9f` | Generated industrial shower (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal | -Y (low) | 5/4 | 1.16 x 0.941 x 1.93 | x1.93001 |
| shower | generated | `gen_shower_japandi_1_dcdcd4dc` | Generated japandi shower (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (low) | 4/4 | 1.22 x 0.898 x 2.03 | x2.02709 |
| shower | generated | `gen_shower_mediterranean_1_4cc815f7` | Generated mediterranean shower (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (low) | 4/4 | 1.15 x 0.948 x 2.06 | x2.05331 |
| shower | generated | `gen_shower_minimal_1_25eeb7e2` | Generated minimal shower (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (low) | 4/4 | 1.25 x 0.874 x 2.16 | x2.1596 |
| shower | generated | `gen_shower_rustic_1_26a99f3f` | Generated rustic shower (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (low) | 4/4 | 1.12 x 0.976 x 1.94 | x1.9317 |
| shower | generated | `gen_shower_scandinavian_1_0ae4a37a` | Generated scandinavian shower (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (low) | 4/4 | 0.984 x 1.11 x 1.94 | x1.93769 |
| bathtub | generated | `gen_bathtub_industrial_1_46aaa4c2` | Generated industrial bathtub (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 1.47 x 0.76 x 0.8 | x1.46692 |
| bathtub | generated | `gen_bathtub_japandi_3_83eb18c0` | Generated japandi bathtub (3) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | +Y (high) | 5/4 | 1.45 x 0.844 x 0.8 | x1.44512 |
| bathtub | generated | `gen_bathtub_mediterranean_1_11d9dbc8` | Generated mediterranean bathtub (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 4/5 | 1.32 x 0.779 x 0.8 | x1.32114 |
| bathtub | generated | `gen_bathtub_minimal_1_fe9cee36` | Generated minimal bathtub (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 5/4 | 1.5 x 0.852 x 0.56 | x1.49802 |
| bathtub | generated | `gen_bathtub_modern_1_009871cf` | Generated modern bathtub (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 1.33 x 0.801 x 0.8 | x1.32594 |
| bathtub | generated | `gen_bathtub_modern_3_0f116dc4` | Generated modern bathtub (3) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 5/4 | 1.48 x 0.867 x 0.794 | x1.47303 |
| bathtub | generated | `gen_bathtub_modern_minimal_1_1a44f6ff` | Generated modern minimal bathtub (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 1.34 x 0.812 x 0.8 | x1.33302 |
| bathtub | generated | `gen_bathtub_modern_minimal_2_927c5b3c` | Generated modern minimal bathtub (2) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 1.31 x 0.717 x 0.8 | x1.30465 |
| bathtub | generated | `gen_bathtub_modern_minimal_3_5f405b34` | Generated modern minimal bathtub (3) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 1.35 x 0.847 x 0.8 | x1.35043 |
| bathtub | generated | `gen_bathtub_scandinavian_1_230fe403` | Generated scandinavian bathtub (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 1.26 x 0.777 x 0.8 | x1.25936 |
| bathtub | generated | `gen_bathtub_scandinavian_2_6fde34a5` | Generated scandinavian bathtub (2) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 1.39 x 0.802 x 0.8 | x1.39271 |
| bathtub | generated | `gen_bathtub_scandinavian_4_a6fdd251` | Generated scandinavian bathtub (4) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 1.32 x 0.737 x 0.8 | x1.32156 |
| bathtub | objaverse | `objaverse_84d5cdc68a674e12958f41500e988502` | CARBAWH1-6DT01 | trendforward | CC-BY-NC-4.0 | non_commercial | modern minimal, minimal, modern | +Y (high) | 5/4 | 1.24 x 1.03 x 0.459 | x2.34595 |
| tv_unit | abo | `abo_B00OGP5S98` | Home Corona 2 unità da 1 TV a schermo Piatto, supporto/ripostigli | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/5 | 1.2 x 0.4 x 0.51 | x1 |
| tv_unit | abo | `abo_B01DA8QJYO` | Amazon Brand - Movian Corona TV Cabinet, Flat Screen Stand Unit, Solid Pine Wood | Amazon.com | CC-BY-4.0 | – | japandi | -Y (high) | 4/5 | 1.08 x 0.44 x 0.55 | x1 |
| tv_unit | abo | `abo_B072ZMT5SD` | Amazon Brand – Rivet King Street Industrial TV Media Console Table with Three Drawers, Black Metal and Wood, Glass | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal | -Y (high) | 5/4 | 1.49 x 0.399 x 0.395 | x1 |
| tv_unit | abo | `abo_B072ZNMKGM` | Amazon Brand – Rivet King Street Industrial Cabinet Media Console Table With Functional Storage, Walnut, Black Metal, Glass | Amazon.com | CC-BY-4.0 | – | japandi, modern minimal, minimal | -Y (high) | 5/4 | 1.2 x 0.399 x 0.8 | x1 |
| tv_unit | abo | `abo_B072ZNPRTC` | Amazon Brand – Rivet King Street Industrial Four-Drawer Media Console Table, Walnut, Black Metal, Glass | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/4 | 1.2 x 0.401 x 0.8 | x1 |
| tv_unit | abo | `abo_B075Z1NM5W` | Amazon Brand – Rivet Eastport Modern Industrial Entertainment Center Console TV Stand Table, 59"W, Oak | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 4/4 | 1.5 x 0.499 x 0.491 | x1 |
| tv_unit | abo | `abo_B075Z8KX9N` | Amazon Brand – Stone & Beam Ferndale Rustic Reclaimed Pine Media TV Console Stand, 71"W, Sandstone | Amazon.com | CC-BY-4.0 | – | japandi, rustic | -Y (high) | 4/5 | 1.8 x 0.453 x 0.573 | x1 |
| tv_unit | abo | `abo_B07B7J5BC2` | Amazon Brand – Stone & Beam Alan Casual Wood Media TV Console Table, 62"W, Washed Navy and Gold | Amazon.com | CC-BY-4.0 | – | modern minimal | -Y (high) | 4/4 | 1.57 x 0.479 x 0.719 | x1 |
| tv_unit | abo | `abo_B07B8FN8TP` | Amazon Brand – Stone & Beam Traditional Oak Wood Media TV Console Table, 59", Walnut Finish | Amazon.com | CC-BY-4.0 | – | classic, rustic | -Y (high) | 5/5 | 1.48 x 0.461 x 0.852 | x1 |
| tv_unit | abo | `abo_B07B8RYY41` | Amazon Brand – Stone & Beam Bruckner Casual Wood Media Table, 64"W, Brown | Amazon.com | CC-BY-4.0 | – | japandi, modern minimal, minimal, modern | -Y (high) | 5/4 | 1.63 x 0.452 x 0.66 | x1 |
| tv_unit | abo | `abo_B07BVHKPFS` | Amazon Brand – Rivet Bowlyn Mid-Century Modern Wood TV Media Table Stand, 64", Walnut | Amazon.com | CC-BY-4.0 | – | japandi, modern | -Y (high) | 5/5 | 1.63 x 0.48 x 0.61 | x1 |
| tv_unit | abo | `abo_B07C9YVDHJ` | Amazon Brand – Rivet Bowlyn Mid-Century Modern Wood TV Media Table Stand, 54", Walnut | Amazon.com | CC-BY-4.0 | – | modern | -Y (high) | 5/4 | 1.37 x 0.48 x 0.61 | x1 |
| tv_unit | abo | `abo_B07DYV7WNN` | ROCKPOINT TV Stand, 42x16x23.6inch, Walnut Brown | Amazon.com | CC-BY-4.0 | – | japandi, rustic | -Y (high) | 4/5 | 1.07 x 0.406 x 0.813 | x1 |
| tv_unit | abo | `abo_B07HSG5DGP` | Amazon Brand – Rivet Roxmere Mid-Century Modern TV Media Console Center Stand, 59"W, Acacia Wood &amp; Dark Metal | Amazon.com | CC-BY-4.0 | – | japandi, modern minimal, industrial | -Y (high) | 5/5 | 1.48 x 0.454 x 0.506 | x1 |
| tv_unit | abo | `abo_B07JGPKSBB` | Amazon Brand - Movian TV Unit with Storage, 40 x 154cm, Oak/Timber/High Gloss White | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 1.55 x 0.4 x 0.44 | x1 |
| tv_unit | abo | `abo_B07K6VT8VN` | Movian TV Board for TVs up to 80 Inches | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/4 | 1.9 x 0.42 x 0.537 | x1 |
| tv_unit | abo | `abo_B07QB8DQ45` | Amazon Brand – Rivet Corban Contemporary 2-Drawer Media Console, 75"W, Gray | Amazon.com | CC-BY-4.0 | – | japandi, modern | -Y (high) | 4/4 | 1.8 x 0.405 x 0.787 | x1 |
| tv_unit | abo | `abo_B07QF9QCZ1` | Amazon Brand – Rivet Corban Contemporary Media Cabinet, 59"W, Gray | Amazon.com | CC-BY-4.0 | – | japandi | -Y (high) | 5/4 | 1.19 x 0.405 x 0.787 | x1 |
| tv_unit | abo | `abo_B07SB8WWHD` | Amazon Brand - Movian 2-Door TV Stand, 150 x 41 x 44 cm, White | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal | -Y (high) | 4/4 | 1.5 x 0.41 x 0.44 | x1 |
| tv_unit | abo | `abo_B07VHNMRY8` | Amazon Brand - Movian 2-Door 1-Shelf TV Stand, 176 x 40 x 58 cm, White and Oak Effect | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/4 | 1.76 x 0.4 x 0.58 | x1 |
| bookshelf | abo | `abo_B074KKXLK1` | Amazon Brand – Stone & Beam Glenwood Bookcase, 72"H, Oak | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal | -Y (high) | 5/4 | 0.539 x 0.395 x 1.73 | x1 |
| bookshelf | abo | `abo_B075Z6YS1Z` | Amazon Brand – Stone & Beam Larson Industrial Wood and Metal 4-Shelf Bookcase, 73"H, Walnut | Amazon.com | CC-BY-4.0 | – | industrial | -Y (high) | 5/4 | 0.874 x 0.359 x 1.86 | x1 |
| bookshelf | abo | `abo_B07B7J2VCD` | Amazon Brand – Stone & Beam Casual Wood Bookcase, 34"W, Natural Rattan | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 5/4 | 0.864 x 0.453 x 1.93 | x1 |
| bookshelf | abo | `abo_B07H8P1N9T` | Amazon Brand - Movian Moselle 2-Door Cabinet/Bookcase with 8 Shelves, 139 x 100 x 45cm, Light Brown Oak-Effect/White | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 5/4 | 1 x 0.45 x 1.39 | x1 |
| bookshelf | abo | `abo_B07H8SQ2NZ` | Amazon Brand - Movian Oker 2-Door Cabinet/Bookcase with 8 Shelves, 100 x 140cm, Light Brown Oak-Effect/White | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 5/4 | 0.995 x 0.434 x 1.4 | x1 |
| bookshelf | abo | `abo_B07HSCJZQM` | Amazon Brand – Rivet Roxmere Modern Ladder Bookcase, 23.6"W, Acacia Wood and Dark Metal | Amazon.com | CC-BY-4.0 | – | modern minimal, industrial | -Y (high) | 4/4 | 0.652 x 0.454 x 2 | x1 |
| bookshelf | abo | `abo_B07HSCNKCT` | Stone & Beam Rylee Modern Bookcase 39.4"Wx76.8”H, Mixed Gray | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/4 | 0.748 x 0.307 x 1.47 | x1 |
| bookshelf | abo | `abo_B07JGY5LNV` | Amazon Brand - Alkove Velle Bookcase, 42 x 95 x 202cm, Oiled Honey Oak | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/5 | 0.95 x 0.42 x 2.02 | x1 |
| bookshelf | abo | `abo_B07PMK78R8` | AmazonBasics Modern 5-Tier Ladder Bookshelf Organizer with Solid Rubber Wood Frame, Espresso | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.6 x 0.35 x 1.77 | x1 |
| bookshelf | abo | `abo_B07PQS58XN` | AmazonBasics Classic 5-Shelf Open Bookcase Organizer with Solid Rubber Wood Frame - Espresso | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.66 x 0.381 x 1.89 | x1 |
| bookshelf | abo | `abo_B07PSZHDNK` | AmazonBasics Classic 5-Tier Open Bookcase with Solid Rubber Wood - Walnut | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.66 x 0.382 x 1.89 | x1 |
| bookshelf | abo | `abo_B07QC876WJ` | Amazon Brand – Rivet Davenport Contemporary Shelf, 34"W, Elm and Metal | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, industrial | -Y (high) | 5/4 | 0.874 x 0.386 x 1.8 | x1 |
| bookshelf | abo | `abo_B082JGV1YM` | Amazon Brand – Stone & Beam 5-Shelf Bookcase, 75"H, Weathered Oak Finish | Amazon.com | CC-BY-4.0 | – | modern | -Y (high) | 4/4 | 0.805 x 0.335 x 1.91 | x1 |
| bookshelf | objaverse | `objaverse_4939d1bca386405f9cc22c48441b63de` | Bookcase | Bec | CC-BY-4.0 | – | modern minimal, industrial | -Y (high) | 5/4 | 0.999 x 0.502 x 1.28 | x1 |
| bookshelf | objaverse | `objaverse_68baafb344b2445a8e7f4917b6fe8a63` | Scaffale B | Francesco Coldesina | CC-BY-4.0 | – | classic | -Y (high) | 5/4 | 1.16 x 0.392 x 1.84 | x0.0069429 |
| bookshelf | objaverse | `objaverse_6c5ac2547db34c3c81b2e4808b000386` | Dusty Old Bookshelf (FREE) | Brandon Westlake | CC-BY-4.0 | – | classic | +Y (high) | 4/4 | 0.92 x 0.387 x 2.08 | x1 |
| bookshelf | objaverse | `objaverse_7a545709aa98429a9b30f812f70193f7` | Bookcase | joseph.casey97 | CC-BY-4.0 | – | modern minimal, minimal | -Y (high) | 5/4 | 1.03 x 0.444 x 1.68 | x0.840344 |
| bookshelf | objaverse | `objaverse_b43c45317fd74a4aa9ba443b9a355ea3` | Bookcase | Icanreed | CC-BY-4.0 | – | modern, neutral | -Y (high) | 5/4 | 1.05 x 0.434 x 1.92 | x0.348837 |
| bookshelf | objaverse | `objaverse_d48a42e91c5d4716a8c254addf8c9d99` | High Bookcase | 8549 | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 5/4 | 1.18 x 0.387 x 1.89 | x7.25457 |
| bookshelf | objaverse | `objaverse_eb98251fbccf4cdd8a3737362e2378e9` | Solo 100シェルフ WN | classe-saga | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 5/5 | 0.965 x 0.29 x 1.04 | x1 |
| nightstand | abo | `abo_B01D3C7Z4A` | Amazon Brand - Hallowood Waverly 1 Drawer Small Side Table in Light Oak Finish | Solid Wooden End/Lamp Stand/Bedside Cabinet/Nightstand, (WAV-LAM590) | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/5 | 0.428 x 0.418 x 0.614 | x1 |
| nightstand | abo | `abo_B072ZMHBKQ` | Amazon Brand – Rivet Mid-Century Modern Lacquer Side End Table Nightstand, Grey and Walnut | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 5/4 | 0.37 x 0.288 x 0.508 | x1 |
| nightstand | abo | `abo_B074KKMQBG` | Amazon Brand – Stone & Beam Cabernet Slatted 3-Drawer Side End Table Nightstand, 18.9"W, Ash | Amazon.com | CC-BY-4.0 | – | modern minimal | -Y (high) | 5/4 | 0.465 x 0.41 x 0.695 | x1 |
| nightstand | abo | `abo_B075X38PZ7` | Amazon Brand – Stone & Beam Newport Nightstand End Table, 22"W, Toffee Oak | Amazon.com | CC-BY-4.0 | – | rustic | -Y (high) | 5/5 | 0.586 x 0.461 x 0.597 | x1 |
| nightstand | abo | `abo_B079VK52WZ` | Amazon Brand - Movian High Gloss 2 Drawer Bedside Cabinet, Black and Walnut, 47 x 40 x 36 cm | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.4 x 0.36 x 0.47 | x1 |
| nightstand | abo | `abo_B079VKDKC1` | Amazon Brand - Movian High Gloss 2 Drawer Bedside Cabinet, White and Walnut, 47 x 40 x 36 cm | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.4 x 0.36 x 0.47 | x1 |
| nightstand | abo | `abo_B079VNKB6Z` | Amazon Brand - Movian High Gloss 3 Drawer Bedside Cabinet, Black and Walnut, 56 x 40 x 36 cm | Amazon.com | CC-BY-4.0 | – | modern minimal, modern | -Y (high) | 5/4 | 0.4 x 0.36 x 0.56 | x1 |
| nightstand | abo | `abo_B079VNL3CG` | Amazon Brand - Movian High Gloss 3 Drawer Bedside Cabinet, Black, 56 x 40 x 36 cm | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal | -Y (high) | 4/4 | 0.4 x 0.36 x 0.56 | x1 |
| nightstand | abo | `abo_B07DVRLW48` | Ravenna Home Priscilla Modern X-Frame End Table Nightstand, 18.9"W | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal | -Y (high) | 4/4 | 0.479 x 0.402 x 0.623 | x1 |
| nightstand | abo | `abo_B07K7K7GTZ` | Amazon Brand - Alkove Hayes 1-Drawer Solid Wood Nightstand, 56 x 44 x 47cm, Wild Oak | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/5 | 0.56 x 0.44 x 0.47 | x1 |
| nightstand | abo | `abo_B07L1DH1PX` | Amazon Brand - Solimo Aquilla Engineered Wood Bedside Table with Drawer (Wenge Finish) | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal | -Y (high) | 5/4 | 0.4 x 0.461 x 0.46 | x1 |
| nightstand | abo | `abo_B07PX3CC31` | AmazonBasics Classic Wood Nightstand End Table with Cabinet - Black Oak | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal | -Y (high) | 4/4 | 0.48 x 0.381 x 0.635 | x1 |
| nightstand | abo | `abo_B07QD6TXWS` | Amazon Brand – Rivet Claremont Contemporary Nightstand with Tapered Legs, 20"W, Pale Wood and White | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 5/4 | 0.571 x 0.407 x 0.61 | x1 |
| nightstand | abo | `abo_B07QS8TBXT` | Amazon Brand Movian Emme, Bedside Table, 40 x 40 x 45 cm (L x W x H), High Gloss White | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal | -Y (high) | 4/4 | 0.399 x 0.404 x 0.447 | x1 |
| nightstand | abo | `abo_B07RNZC4TJ` | AmazonBasics 2-Drawer Bedside Table, 45 x 38 x 49 cm, Light Brown/Dark Grey | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 4/4 | 0.45 x 0.38 x 0.5 | x1 |
| nightstand | abo | `abo_B07RPZSM4W` | AmazonBasics - 1-Drawer 1-Shelf Bedside Table, 45 x 38 x 53 cm, Beige with Grey Drawer | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/4 | 0.45 x 0.38 x 0.53 | x1 |
| nightstand | abo | `abo_B07VB7Q6W7` | Amazon Brand - Movian Kyyvesi, 2-Drawer Storage Night Stand, 60 x 42 x 50 cm, Walnut Effect | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/5 | 0.6 x 0.42 x 0.5 | x1 |
| nightstand | abo | `abo_B084MYDTKM` | Amazon Brand - Rivet Mango Wood and Iron 3-Drawer Shutter Nightstand, 18"W, Natural Finish | Amazon.com | CC-BY-4.0 | – | japandi, modern minimal, minimal, rustic | -Y (high) | 5/5 | 0.457 x 0.406 x 0.559 | x1 |
| dresser | abo | `abo_B00838756S` | Vida Designs Corona Merchant Chest Of Drawers, 9 Drawer, Solid Pine Wood | Amazon.com | CC-BY-4.0 | – | rustic, neutral | -Y (high) | 4/4 | 0.99 x 0.41 x 0.74 | x1 |
| dresser | abo | `abo_B009S7IZWG` | Amazon Brand - Movian Corona Sideboard, 1 Door 4 Drawer, Solid Pine Wood, 76 x 86 x 40 cm | Amazon.com | CC-BY-4.0 | – | rustic | -Y (high) | 4/4 | 0.915 x 0.44 x 0.835 | x1 |
| dresser | abo | `abo_B01557QQSW` | Marchio Amazon - Movian, credenze modello Minho, 98 x 90 x 38 cm, quercia Sanremo | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 4/4 | 0.98 x 0.38 x 0.9 | x1 |
| dresser | abo | `abo_B01MG6BPC6` | Vida Designs Corona Chest Of Drawers, 4 Drawer, Rustic, Solid Pine Wood. | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 4/4 | 0.8 x 0.41 x 0.73 | x1 |
| dresser | abo | `abo_B071FJR3S6` | Amazon Brand – Stone & Beam Glenwood Industrial Metal Dresser, 60"W, Oak | Amazon.com | CC-BY-4.0 | – | modern minimal | -Y (high) | 5/5 | 1.65 x 0.623 x 1.06 | x1 |
| dresser | abo | `abo_B071FJR3SR` | Amazon Brand – Stone & Beam Glenwood Industrial Metal Chest of Drawers, 52"H, Oak | Amazon.com | CC-BY-4.0 | – | modern minimal | -Y (high) | 5/4 | 0.965 x 0.508 x 1.32 | x1 |
| dresser | abo | `abo_B071FJR479` | Amazon Brand – Rivet West, Mid-Century, Oak Distinct Grain, 6-Drawer Dresser, 60"W, Dark Oak Finish | Amazon.com | CC-BY-4.0 | – | modern minimal, modern | -Y (high) | 5/4 | 1.52 x 0.512 x 0.889 | x1 |
| dresser | abo | `abo_B071P9WJBT` | Amazon Brand – Stone & Beam Parson 6-Drawer Wood Bedroom Dresser, 60"W, Natural | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern, rustic, neutral | -Y (high) | 5/5 | 1.66 x 0.564 x 0.932 | x1 |
| dresser | abo | `abo_B071SHBTM5` | Amazon Brand – Rivet West, Mid-Century, Oak Distinct Grain Chest Bedroom Dresser, 38"W, Dark Oak Finish | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal | -Y (high) | 5/4 | 0.964 x 0.516 x 1.32 | x1 |
| dresser | abo | `abo_B075YZYJQN` | Amazon Brand – Rivet Eastport Industrial Wood Dresser, 30"W, Oak Finish | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/5 | 0.761 x 0.479 x 1.24 | x1 |
| dresser | abo | `abo_B079X4CP3F` | Amazon Brand - Movian Hulio High Gloss 4 Drawer Chest Of Drawers, Black and Walnut, 72 x 75 x 36 cm | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.75 x 0.36 x 0.72 | x1 |
| dresser | abo | `abo_B07B4VXZZC` | Amazon Brand – Stone & Beam Gould Contemporary Wood Bedroom Dresser Chest, 18", Washed Navy and Gold | Amazon.com | CC-BY-4.0 | – | classic | -Y (high) | 4/4 | 1.05 x 0.463 x 0.986 | x1 |
| dresser | abo | `abo_B07FFWSBBF` | Artum Hill BE6-802 Laurel Dresser, 5-Drawer, Modern Gray | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 5/4 | 1.02 x 0.457 x 1.22 | x1 |
| dresser | abo | `abo_B07FK1HLZ4` | Artum Hill BE5-539 Kensington Dresser, 6-Drawer, Limestone Gray | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern, rustic | -Y (high) | 4/4 | 1.63 x 0.457 x 1.02 | x1 |
| dresser | abo | `abo_B07HSDP2CP` | Amazon Brand – Rivet Modern Chest of Drawers with Diamond Pattern 17.3"W, Walnut &amp; Gray Wash | Amazon.com | CC-BY-4.0 | – | modern | -Y (high) | 5/4 | 0.967 x 0.446 x 0.847 | x1 |
| dresser | abo | `abo_B07HSH4WFB` | Amazon Brand – Rivet Modern Chest of Drawers with Diamond Pattern, 17.7 Inch Width, Natural | Amazon.com | CC-BY-4.0 | – | modern, industrial | -Y (high) | 5/4 | 0.923 x 0.453 x 0.801 | x1 |
| dresser | abo | `abo_B07PVBJ7X8` | Ameriwood Home Classic 6 Drawer Dresser, Espresso | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 1.36 x 0.401 x 0.755 | x1 |
| dresser | abo | `abo_B07PYKPBY9` | Ameriwood Home Classic 5 Drawer Dresser, Espresso | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.704 x 0.418 x 1.25 | x1 |
| washing_machine | generated | `gen_washing_machine_classic_1_dffff7e0` | Generated classic washing machine (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.642 x 0.608 x 0.89 | x0.888386 |
| washing_machine | generated | `gen_washing_machine_industrial_1_b7c9d275` | Generated industrial washing machine (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, modern | -Y (high) | 4/5 | 0.591 x 0.661 x 0.896 | x0.893922 |
| washing_machine | generated | `gen_washing_machine_japandi_1_f1f4def2` | Generated japandi washing machine (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.623 x 0.627 x 0.854 | x0.852118 |
| washing_machine | generated | `gen_washing_machine_japandi_2_d8b8ac48` | Generated japandi washing machine (2) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.635 x 0.615 x 0.88 | x0.878831 |
| washing_machine | generated | `gen_washing_machine_japandi_3_3e2ddcc7` | Generated japandi washing machine (3) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.585 x 0.668 x 0.84 | x0.837891 |
| washing_machine | generated | `gen_washing_machine_mediterranean_1_bffe5bde` | Generated mediterranean washing machine (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.606 x 0.645 x 0.828 | x0.833306 |
| washing_machine | generated | `gen_washing_machine_minimal_1_9ec6e746` | Generated minimal washing machine (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.614 x 0.636 x 0.855 | x0.853547 |
| washing_machine | generated | `gen_washing_machine_modern_1_f4bdd46e` | Generated modern washing machine (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, modern | -Y (high) | 5/4 | 0.601 x 0.65 x 0.843 | x0.84142 |
| washing_machine | generated | `gen_washing_machine_modern_2_379d2585` | Generated modern washing machine (2) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.617 x 0.633 x 0.855 | x0.853454 |
| washing_machine | generated | `gen_washing_machine_modern_3_50bfae6f` | Generated modern washing machine (3) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.604 x 0.646 x 0.833 | x0.831489 |
| washing_machine | generated | `gen_washing_machine_modern_minimal_1_07b2b182` | Generated modern minimal washing machine (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.619 x 0.631 x 0.901 | x0.89986 |
| washing_machine | generated | `gen_washing_machine_modern_minimal_2_94b29e08` | Generated modern minimal washing machine (2) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.639 x 0.611 x 0.876 | x0.873972 |
| washing_machine | generated | `gen_washing_machine_modern_minimal_3_ff74255c` | Generated modern minimal washing machine (3) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.684 x 0.552 x 0.95 | x0.948281 |
| washing_machine | generated | `gen_washing_machine_rustic_1_c7990bb9` | Generated rustic washing machine (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.632 x 0.618 x 0.881 | x0.878838 |
| washing_machine | generated | `gen_washing_machine_scandinavian_1_0a5054b6` | Generated scandinavian washing machine (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.602 x 0.649 x 0.857 | x0.856454 |
| washing_machine | generated | `gen_washing_machine_scandinavian_2_67f28c86` | Generated scandinavian washing machine (2) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.627 x 0.623 x 0.837 | x0.837225 |
| washing_machine | generated | `gen_washing_machine_scandinavian_3_292e2d11` | Generated scandinavian washing machine (3) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.574 x 0.709 x 0.8 | x0.798718 |
| washing_machine | generated | `gen_washing_machine_scandinavian_4_d66cae6a` | Generated scandinavian washing machine (4) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.584 x 0.669 x 0.812 | x0.811091 |
| side_table | abo | `abo_B01N3MBCKT` | Ameriwood Home Carver End Table, Gray/Sonoma Oak | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (low) | 5/4 | 0.506 x 0.504 x 0.587 | x1 |
| side_table | abo | `abo_B072ZKPK7J` | Amazon Brand – Rivet Mid-Century Modern Round Black Wood Nesting Side End Table, 15.7" W, Dark Oak | Amazon.com | CC-BY-4.0 | – | modern minimal | -Y (low) | 5/5 | 0.399 x 0.399 x 0.46 | x1 |
| side_table | abo | `abo_B075Z8627Z` | Amazon Brand – Stone & Beam Larson Industrial Wood & Metal Side End Table, 27"W, Walnut | Amazon.com | CC-BY-4.0 | – | industrial, rustic | -Y (low) | 5/5 | 0.678 x 0.524 x 0.613 | x1 |
| side_table | abo | `abo_B075Z8KX91` | Amazon Brand – Stone & Beam Ferndale Rustic Reclaimed Pine Side End Table, 24"W, Sandstone | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, rustic | -Y (low) | 5/5 | 0.61 x 0.61 x 0.457 | x1 |
| side_table | abo | `abo_B075Z8TDQ6` | Amazon Brand – Stone & Beam Modern Rustic Reclaimed Elm Round Accent Side End Table, 16.9"W, Natural | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, minimal, modern, neutral | -Y (low) | 5/5 | 0.432 x 0.431 x 0.46 | x1 |
| side_table | abo | `abo_B075ZBW1QM` | Stone & Beam Larson Industrial Wood & Metal Side End Table, 22"W, Set of 2, Walnut | Amazon.com | CC-BY-4.0 | – | industrial, rustic | -Y (low) | 5/5 | 0.548 x 0.553 x 0.482 | x1 |
| side_table | abo | `abo_B07B7J5XSQ` | Amazon Brand – Rivet Modern Round Metal Side End Accent Table, 15"W, Black | Amazon.com | CC-BY-4.0 | – | modern minimal, modern | -Y (low) | 5/5 | 0.403 x 0.415 x 0.548 | x1 |
| side_table | abo | `abo_B07B7J8CGH` | Amazon Brand – Rivet Mid-Century Modern Honeycomb Square End/Side/Nesting Tables, Wood and Bronze | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (low) | 5/5 | 0.505 x 0.762 x 0.505 | x1 |
| side_table | abo | `abo_B07B7J8FV9` | Amazon Brand – Rivet Modern White Marble and Wood Double Storage Wood Shelf Side End Table, 21.3"H, White/Brass/Walnut | Amazon.com | CC-BY-4.0 | – | scandinavian, minimal, modern | -Y (low) | 5/5 | 0.43 x 0.456 x 0.493 | x1 |
| side_table | abo | `abo_B07B7J8HFV` | Amazon Brand – Rivet Modern Square Nesting End/Side Tables, Black Metal and Tempered Mirror Glass | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal | -Y (low) | 5/4 | 0.508 x 0.788 x 0.54 | x1 |
| side_table | abo | `abo_B07DB92DKW` | Amazon Brand – Ravenna Home Aubree Mid-Century Modern Shelf Storage Side Table, 23.6"W, Grey pine | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, industrial | -Y (low) | 5/5 | 0.3 x 0.599 x 0.701 | x1 |
| side_table | abo | `abo_B07DMHP1ZY` | 2L Lifestyle Harbor Modern Wedge Side End Table,Brown | Amazon.com | CC-BY-4.0 | – | minimal, modern | -Y (low) | 5/4 | 0.399 x 0.605 x 0.589 | x1 |
| side_table | abo | `abo_B07F3XLTRH` | Amazon Brand – Ravenna Home Anne Marie Wood Curved Leg Shelf Storage Side End Table, 20"W, Black | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (low) | 4/5 | 0.508 x 0.457 x 0.457 | x1 |
| side_table | abo | `abo_B07H2J7689` | Ball & Cast End Table | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern, rustic, neutral | -Y (low) | 5/4 | 0.66 x 0.559 x 0.635 | x1 |
| side_table | abo | `abo_B07HSCRGTJ` | Amazon Brand – Stone & Beam 2-Tier Rustic Accent End Table, 26"W, Light Wood and Dark Metal | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern, industrial | -Y (low) | 5/5 | 0.629 x 0.628 x 0.684 | x1 |
| side_table | abo | `abo_B07M6PKCM3` | Amazon Brand – Ravenna Home Damask-Pattern Ceramic Garden Stool or Side Table, 16"H, Grey | Amazon.com | CC-BY-4.0 | – | classic | -Y (low) | 5/4 | 0.309 x 0.309 x 0.397 | x1 |
| side_table | abo | `abo_B07MBFDHRY` | Amazon Brand – Ravenna Home Clover-Pattern Ceramic Garden Stool or Side Table, 16"H, Grey | Amazon.com | CC-BY-4.0 | – | modern | -Y (low) | 5/5 | 0.352 x 0.349 x 0.387 | x1 |
| side_table | abo | `abo_B07MF1TQYR` | Amazon Brand – Ravenna Home Moroccan-Pattern Ceramic Garden Stool or Side Table, 16"H, Grey | Amazon.com | CC-BY-4.0 | – | japandi | -Y (low) | 5/5 | 0.325 x 0.325 x 0.388 | x1 |
| side_table | abo | `abo_B07QGFZ2B4` | Amazon Brand – Rivet Industrial Mango-Topped Side Table, 19.61"W | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, industrial | -Y (low) | 5/5 | 0.499 x 0.498 x 0.55 | x1 |
| side_table | abo | `abo_B07W5648MH` | Amazon Brand - Rivet Round End/Side Table with 2 Shelves, 40 x 40 x 61 cm, Pine Wood with Walnut-Colour Lacquer/Metal | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (low) | 5/5 | 0.4 x 0.4 x 0.61 | x1 |
| floor_lamp | abo | `abo_B07374K536` | Amazon Brand – Rivet Caden Adjustable Task Floor Lamp with Bulb, 60"H, Black and Brass | Amazon.com | CC-BY-4.0 | – | modern, industrial | -Y (low) | 5/4 | 0.235 x 0.618 x 1.63 | x1 |
| floor_lamp | abo | `abo_B07374SBFN` | Amazon Brand – Stone & Beam Glass Column Brass Floor Lamp, With Bulb, Linen Shade, 13.0" x 13.0" x 59.0", Brushed Brass | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (low) | 4/5 | 0.42 x 0.42 x 1.48 | x1 |
| floor_lamp | abo | `abo_B073P25SXR` | Rivet Mid-Century Modern Theory 5-Arm Living Room Floor Lamp with Edison Light Bulbs, 60"H, Black and Brass Finish | Amazon.com | CC-BY-4.0 | – | industrial | -Y (low) | 5/4 | 0.599 x 0.572 x 1.72 | x1 |
| floor_lamp | abo | `abo_B073P3HHFT` | Rivet Adjustable Tree-Style 3-Light Floor Lamp, 69"H, with Bulbs, Bronze and Brass | Amazon.com | CC-BY-4.0 | – | industrial | -Y (low) | 4/4 | 0.415 x 0.428 x 1.72 | x1 |
| floor_lamp | abo | `abo_B073P3S1NX` | Rivet Olive 4 Wood Shelf Standing Floor Lamp With Light Bulb and USB Charging Station - 11.8 x 11.8 x 62 Inches, Brass | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (low) | 4/4 | 0.31 x 0.308 x 1.57 | x1 |
| floor_lamp | abo | `abo_B07B4ZK8BR` | Amazon Brand – Rivet Mid-Century Modern Floor Lamp with Wireless USB Port Charging Wood Table, 59"H, Light Bulb Included, Black | Amazon.com | CC-BY-4.0 | – | scandinavian, minimal, modern | -Y (low) | 5/4 | 0.573 x 0.573 x 1.52 | x1 |
| floor_lamp | abo | `abo_B07DBHCKML` | Amazon Brand – Ravenna Home Traditional Standing Floor Lamp with Reading Light and LED Light Bulb - 69.75 Inches, Brushed Nickel with Frosted Glass | Amazon.com | CC-BY-4.0 | – | modern | -Y (low) | 5/4 | 0.575 x 0.406 x 1.79 | x1 |
| floor_lamp | abo | `abo_B07DBK7KKZ` | Amazon Brand – Ravenna Home Frosted Glass Living Room Standing Floor Lamp with LED Light Bulb - 69.75 Inches, Brushed Nickel | Amazon.com | CC-BY-4.0 | – | classic | -Y (low) | 4/5 | 0.406 x 0.406 x 1.77 | x1 |
| floor_lamp | abo | `abo_B07HK8NDXS` | Amazon Brand – Stone & Beam Rustic Storage Space/Shelving Unit Pull Chain Switch Floor Lamp with Bulb, 62"H, Black | Amazon.com | CC-BY-4.0 | – | modern minimal, industrial | -Y (low) | 4/4 | 0.427 x 0.384 x 1.47 | x1 |
| floor_lamp | abo | `abo_B07HKF59YX` | Amazon Brand – Stone & Beam Mid-Century Modern Henley Living Room Standing Floor Lamp with LED Light Bulb - 15 x 15 x 58 Inches, Matte Black and Antique Brass | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (low) | 5/5 | 0.404 x 0.404 x 1.52 | x1 |
| floor_lamp | abo | `abo_B07MBFDWY5` | Amazon Brand – Ravenna Home Floor Lamp with Shelves, LED Light Bulb included, 62.75"H, Black | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (low) | 4/4 | 0.279 x 0.279 x 1.59 | x1 |
| floor_lamp | abo | `abo_B0824FJCWG` | Amazon Brand – Ravenna Home Traditional Metal Floor Lamp with Stacked Oval Accents, LED Bulb Included, 58.5"H, Polished Nickel | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (low) | 4/5 | 0.356 x 0.356 x 1.49 | x1 |
| floor_lamp | generated | `gen_floor_lamp_japandi_1_4be1c62d` | Generated japandi floor lamp (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | scandinavian, modern minimal, minimal, modern | -Y (low) | 4/5 | 0.455 x 0.455 x 1.2 | x1.19754 |
| floor_lamp | generated | `gen_floor_lamp_japandi_2_ef5fd39d` | Generated japandi floor lamp (2) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | scandinavian, modern minimal, minimal, modern | -Y (low) | 4/5 | 0.568 x 0.565 x 1.2 | x1.19792 |
| floor_lamp | objaverse | `objaverse_01c53767c1f84f55ad9f46eb89949cf9` | Street Lamp | emelyarules | CC-BY-4.0 | – | classic | -Y (low) | 4/4 | 0.332 x 0.381 x 2.1 | x0.61174 |
| floor_lamp | objaverse | `objaverse_0a34dc814a3a44cfa76388e732c05376` | Lamppost | martn00 | CC-BY-4.0 | – | classic | -Y (low) | 4/4 | 0.359 x 0.359 x 2.1 | x0.179861 |
| floor_lamp | objaverse | `objaverse_0eba4ad785674d3586aafc82854100fa` | lamp | anish_ | CC-BY-4.0 | – | classic | -Y (low) | 4/5 | 0.585 x 0.61 x 1.2 | x0.0434402 |
| floor_lamp | objaverse | `objaverse_33eb258d9873435690254cfbb0ea46ec` | Floor Lamp | bilgehan.korkmaz | CC-BY-4.0 | – | modern | -Y (low) | 4/5 | 0.517 x 0.517 x 2 | x1 |
| floor_lamp | objaverse | `objaverse_53409613b45b42b98b979f12ab8faa12` | low poly Lamp 3d model | mohamedvfx | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (low) | 4/4 | 0.518 x 0.518 x 1.2 | x0.00427403 |
| floor_lamp | objaverse | `objaverse_71853da424aa4b208e14f6cf430339ae` | Street lights | U-like | CC-BY-4.0 | – | industrial, classic | -Y (low) | 5/4 | 0.349 x 0.349 x 2.1 | x1.74412 |
| potted_plant | generated | `gen_potted_plant_industrial_2_eb3d21f5` | Generated industrial potted plant (2) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (low) | 4/5 | 0.489 x 0.488 x 1 | x1 |
| potted_plant | generated | `gen_potted_plant_japandi_1_63c10a71` | Generated japandi potted plant (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (low) | 4/5 | 0.45 x 0.478 x 1 | x1 |
| potted_plant | generated | `gen_potted_plant_japandi_2_9a3effd1` | Generated japandi potted plant (2) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | scandinavian, japandi, modern minimal, minimal, modern, neutral | -Y (low) | 4/5 | 0.51 x 0.436 x 0.994 | x1 |
| potted_plant | generated | `gen_potted_plant_japandi_3_36d34f2a` | Generated japandi potted plant (3) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | scandinavian, japandi, modern minimal, minimal, modern, neutral | -Y (low) | 4/5 | 0.521 x 0.526 x 1 | x1 |
| potted_plant | generated | `gen_potted_plant_mediterranean_1_38a58433` | Generated mediterranean potted plant (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | scandinavian, japandi, modern minimal, minimal, modern, mediterranean, neutral | -Y (low) | 4/5 | 0.497 x 0.449 x 1 | x1 |
| potted_plant | generated | `gen_potted_plant_minimal_1_5cf2e7a2` | Generated minimal potted plant (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, modern, neutral | -Y (low) | 4/5 | 0.491 x 0.527 x 0.999 | x1 |
| potted_plant | generated | `gen_potted_plant_modern_1_8fbfec3c` | Generated modern potted plant (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | neutral | -Y (low) | 4/5 | 0.56 x 0.524 x 1 | x1 |
| potted_plant | generated | `gen_potted_plant_modern_minimal_1_6b4ad5f1` | Generated modern minimal potted plant (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | scandinavian, modern minimal, minimal, modern | -Y (low) | 4/5 | 0.509 x 0.512 x 0.995 | x1 |
| potted_plant | generated | `gen_potted_plant_rustic_1_978e47a9` | Generated rustic potted plant (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | scandinavian, japandi, modern minimal, minimal, modern, neutral | -Y (low) | 4/5 | 0.531 x 0.531 x 1 | x1 |
| potted_plant | generated | `gen_potted_plant_scandinavian_1_04f97c4b` | Generated scandinavian potted plant (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | scandinavian, modern minimal, minimal, modern | -Y (low) | 4/5 | 0.573 x 0.556 x 1 | x1 |
| potted_plant | generated | `gen_potted_plant_scandinavian_2_98f7bbd2` | Generated scandinavian potted plant (2) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | scandinavian, modern minimal, minimal, modern | -Y (low) | 4/5 | 0.488 x 0.448 x 1 | x1 |
| potted_plant | generated | `gen_potted_plant_scandinavian_3_ef4f2d99` | Generated scandinavian potted plant (3) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (low) | 4/5 | 0.504 x 0.557 x 1 | x1 |
| potted_plant | objaverse | `objaverse_41e58efcf647494483f9860df99acf60` | Empty Flower Pot | dumerlot | CC-BY-4.0 | – | mediterranean, rustic | -Y (low) | 4/5 | 0.598 x 0.602 x 0.487 | x2.0673 |
| potted_plant | objaverse | `objaverse_57972124483145b4a4bbf4fd4caca6e7` | succulent | Elif Smbl | CC-BY-4.0 | – | modern minimal, minimal | -Y (low) | 4/4 | 0.617 x 0.583 x 0.612 | x0.240114 |
| potted_plant | objaverse | `objaverse_71b53eaee72e4a829a9256a7bcfb7dab` | Cacti pot | Spacyy | CC-BY-4.0 | – | rustic | -Y (low) | 4/4 | 0.222 x 0.234 x 0.305 | x0.0254 |
| potted_plant | objaverse | `objaverse_9dd44cda400c48a083ffd9480067f04f` | Succulent | mika.rr | CC-BY-4.0 | – | modern minimal, minimal | -Y (low) | 4/5 | 0.497 x 0.497 x 0.512 | x0.0254 |
| potted_plant | objaverse | `objaverse_b99c584dd11d4691b5d13303383371e5` | FlowerPot | ibrahmcingi | CC-BY-4.0 | – | mediterranean | -Y (low) | 4/4 | 0.6 x 0.6 x 0.58 | x0.0027579 |
| potted_plant | objaverse | `objaverse_bf122cd0854e422bb94704552c64810b` | CGT 116 Wk8 Plant | mlin234 | CC-BY-4.0 | – | minimal, modern | -Y (low) | 4/4 | 0.238 x 0.261 x 0.361 | x0.0254 |
| cushion | abo | `abo_B074VLRP5T` | Amazon Brand – Rivet Velvet Texture Decorative Throw Pillow, 17" x 17", Midnight | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern, neutral | -Y (low) | 5/5 | 0.432 x 0.246 x 0.414 | x1 |
| cushion | abo | `abo_B074VLRP9S` | Amazon Brand – Stone & Beam Striated Velvet Linen-Look Decorative Throw Pillow, 17" x 17", Midnight | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal | -Y (low) | 4/4 | 0.452 x 0.204 x 0.439 | x1 |
| cushion | abo | `abo_B079TXJNJD` | Amazon Brand – Rivet Modern Geometric Decorative Print Throw Pillow, 20" x 20", Teal | Amazon.com | CC-BY-4.0 | – | modern, neutral | -Y (low) | 5/4 | 0.517 x 0.158 x 0.508 | x1 |
| cushion | abo | `abo_B079TXJV32` | Amazon Brand – Stone & Beam Mojave-Inspired Decorative Throw Pillow Cover, 20" x 20", Black and Red | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern, neutral | -Y (low) | 5/5 | 0.503 x 0.182 x 0.506 | x1 |
| cushion | abo | `abo_B079V39VG5` | Amazon Brand – Stone & Beam Transitional Woven Diamond Decorative Throw Pillow, 20" x 20", Indigo | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern, neutral | -Y (low) | 5/5 | 0.435 x 0.148 x 0.428 | x1 |
| cushion | abo | `abo_B079V3WDY9` | Amazon Brand – Stone & Beam Transitional Woven Diamond Decorative Throw Pillow Cover, 20" x 20", Indigo | Amazon.com | CC-BY-4.0 | – | scandinavian, neutral | -Y (low) | 5/5 | 0.511 x 0.162 x 0.503 | x1 |
| cushion | abo | `abo_B079V3YG6X` | Amazon Brand – Rivet Modern Geometric Decorative Print Pillow Cover, 20" x 20", Black | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (low) | 5/4 | 0.517 x 0.158 x 0.508 | x1 |
| cushion | abo | `abo_B079V6V6TF` | Amazon Brand – Rivet Modern Geometric Decorative Print Pillow Cover, 20" x 20", Teal | Amazon.com | CC-BY-4.0 | – | modern, neutral | -Y (low) | 5/4 | 0.517 x 0.158 x 0.508 | x1 |
| cushion | abo | `abo_B079V9CJB5` | Amazon Brand – Stone & Beam Yard-Dyed Shibori Decorative Throw Pillow Cover, 17" x 17", Blue | Amazon.com | CC-BY-4.0 | – | scandinavian, neutral | -Y (low) | 5/4 | 0.425 x 0.133 x 0.435 | x1 |
| cushion | abo | `abo_B07BMQ64HR` | Amazon Brand – Rivet Abstract Geometric Throw Pillow Cover, 20" x 20", Ivory | Amazon.com | CC-BY-4.0 | – | neutral | -Y (low) | 5/5 | 0.525 x 0.18 x 0.498 | x1 |
| cushion | abo | `abo_B07BMT4F21` | Amazon Brand – Rivet Modern Abstract Geometric Decorative Throw Pillow, 20" x 20", Cover Only, Purple | Amazon.com | CC-BY-4.0 | – | modern, neutral | -Y (low) | 5/4 | 0.503 x 0.208 x 0.496 | x1 |
| cushion | abo | `abo_B07BMTN6GF` | Amazon Brand – Rivet Abstract Geometric Throw Pillow, 20" x 20", Ivory | Amazon.com | CC-BY-4.0 | – | neutral | -Y (low) | 5/5 | 0.502 x 0.21 x 0.503 | x1 |
| cushion | abo | `abo_B07BMTNH22` | Amazon Brand – Rivet Modern Abstract Geometric Decorative Throw Pillow, 20" x 20", Purple | Amazon.com | CC-BY-4.0 | – | modern, neutral | -Y (low) | 5/4 | 0.503 x 0.208 x 0.496 | x1 |
| cushion | abo | `abo_B07BMTXHSR` | Amazon Brand – Rivet Modern Retro Flair Mosaic Geometric Decorative Throw Pillow, 20" x 20", Cover Only, Blue | Amazon.com | CC-BY-4.0 | – | modern, neutral | -Y (low) | 5/4 | 0.503 x 0.208 x 0.496 | x1 |
| cushion | abo | `abo_B07C8MSZ5T` | Amazon Brand – Rivet Modern Abstract Circle Throw Pillow Cover - 20 x 20 Inch, Grey | Amazon.com | CC-BY-4.0 | – | modern | -Y (low) | 4/4 | 0.514 x 0.163 x 0.513 | x1 |
| cushion | abo | `abo_B07C8MT64T` | Amazon Brand – Rivet Modern Mosaic Throw Pillow - 20 x 20 Inch, Blue | Amazon.com | CC-BY-4.0 | – | modern, neutral | -Y (low) | 5/4 | 0.503 x 0.208 x 0.496 | x1 |
| cushion | abo | `abo_B07C8WCWWK` | Amazon Brand – Rivet Abstract Pattern Throw Pillow Cover - 20 x 20 Inch, Grey | Amazon.com | CC-BY-4.0 | – | modern, neutral | -Y (low) | 5/5 | 0.552 x 0.193 x 0.509 | x1 |
| cushion | abo | `abo_B07JKJSJB1` | Amazon Brand – Stone & Beam Casual Pom-Pom Throw Pillow - 24 x 12 Inch, Mineral | Amazon.com | CC-BY-4.0 | – | scandinavian, neutral | -Y (low) | 5/4 | 0.709 x 0.201 x 0.322 | x1 |
| cushion | abo | `abo_B07JKJSTVJ` | Amazon Brand – Rivet Modern Macrame Fringe Lumbar Throw Pillow - 18 x 12 Inch, White | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, neutral | -Y (low) | 4/4 | 0.466 x 0.0838 x 0.305 | x1 |
| cushion | abo | `abo_B07M6PJ4LX` | Ravenna Home Casual Floral Throw Pillow, 20" x 20", Cream and Blue | Amazon.com | CC-BY-4.0 | – | scandinavian, neutral | -Y (low) | 5/5 | 0.526 x 0.166 x 0.507 | x1 |
| rug | abo | `abo_B0714MJKX2` | Amazon Brand – Rivet Shaggy Short Rug, 7'7" x 9'7", Ivory | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern, neutral | -Y (low) | 4/5 | 2.53 x 2.01 x 0.0477 | x1 |
| rug | abo | `abo_B0714MJLTB` | Amazon Brand – Stone & Beam Mid-Century Modern Dusk Wool Rug, 5' x 8', Tan | Amazon.com | CC-BY-4.0 | – | classic | -Y (low) | 5/4 | 2.44 x 1.53 x 0.0104 | x1 |
| rug | abo | `abo_B0714MMHBL` | Rivet Woven Bordered Sisal Area Rug, 3' 6'' x 5' 6'', Natural | Amazon.com | CC-BY-4.0 | – | neutral | -Y (low) | 4/4 | 1.67 x 1.06 x 0.0118 | x1 |
| rug | abo | `abo_B0719STF79` | Amazon Brand – Rivet Diamond Trellis Tassel Wool Rug, 7'6" x 9'6", Ivory | Amazon.com | CC-BY-4.0 | – | scandinavian, neutral | -Y (low) | 4/4 | 3.22 x 2.34 x 0.0262 | x1 |
| rug | abo | `abo_B0719STLSH` | Stone & Beam MFL nuLoom Rug B0719STLSH 5'X8' Cream | Amazon.com | CC-BY-4.0 | – | neutral | -Y (low) | 4/4 | 2.44 x 1.52 x 0.011 | x1 |
| rug | abo | `abo_B071FJZVPH` | Amazon Brand – Rivet Modern Wave Cosmopolitan Area Rug, 8 x 10 Foot, Beige | Amazon.com | CC-BY-4.0 | – | neutral | -Y (low) | 4/4 | 2.58 x 2.07 x 0.0105 | x1 |
| rug | abo | `abo_B071W2XLSC` | nuLOOM Leaflet Fountain Boho Wool Area Rug, 7' 6" x 9' 6", Pink | Amazon.com | CC-BY-4.0 | – | classic | -Y (low) | 4/4 | 2.93 x 2.3 x 0.0116 | x1 |
| rug | abo | `abo_B0735RHGTB` | Amazon Brand – Stone & Beam Swirling Paisley Farmhouse Motif Wool Runner Rug, 2' 6" x 8', Multi | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, neutral | -Y (low) | 4/4 | 2.68 x 0.763 x 0.0149 | x1 |
| rug | abo | `abo_B07B4SDLJM` | Amazon Brand – Rivet Contemporary Striated Jute Area Rug, 10' 6" x 8', Oatmeal | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (low) | 4/4 | 3.2 x 2.43 x 0.045 | x1 |
| rug | abo | `abo_B07B4SDNQT` | Amazon Brand – Rivet Contemporary Striated Jute Rug, 7' 5" x 5' 3", Brick | Amazon.com | CC-BY-4.0 | – | neutral | -Y (low) | 4/4 | 2.11 x 1.59 x 0.0087 | x1 |
| rug | abo | `abo_B07B4SDVG3` | Amazon Brand – Rivet Contemporary Diamond Patterned Area Rug, 7'4" x 5'3", Grey Ivory | Amazon.com | CC-BY-4.0 | – | neutral | -Y (low) | 4/4 | 2.24 x 1.59 x 0.008 | x1 |
| rug | abo | `abo_B07B4SF23K` | Amazon Brand – Rivet Geometric Wool Area Rug, 5 x 8 Foot, Blue, Ivory | Amazon.com | CC-BY-4.0 | – | neutral | -Y (low) | 4/4 | 2.45 x 1.54 x 0.0118 | x1 |
| rug | abo | `abo_B07B4WGGZR` | Amazon Brand – Rivet Contemporary Striated Jute Rug, 13' x 9' 3", Aegean Blue | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern, neutral | -Y (low) | 4/4 | 1.79 x 1.16 x 0.0252 | x1 |
| rug | abo | `abo_B07B4WH5LV` | Amazon Brand – Rivet Contemporary Striated Jute Area Rug, 5' 9" x 3' 9", Silver Birch | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern, neutral | -Y (low) | 4/4 | 1.77 x 1.15 x 0.0213 | x1 |
| rug | abo | `abo_B07B4WKLZ7` | Amazon Brand – Rivet Modern Chevron Wool Area Rug, 5' x 8', Blue, Green, Ivory | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (low) | 4/4 | 2.43 x 1.51 x 0.0066 | x1 |
| rug | abo | `abo_B07B4WKQHJ` | Amazon Brand – Rivet Contemporary Striated Jute Area Rug, 10' 6" x 8', Off White | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal | -Y (low) | 5/4 | 3.24 x 2.47 x 0.0456 | x1 |
| rug | abo | `abo_B07B515Q7D` | Amazon Brand – Rivet Contemporary Striated Jute Rug, 10' 6" x 8', Citron | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal | -Y (low) | 4/4 | 3.2 x 2.43 x 0.0159 | x1 |
| rug | abo | `abo_B07HSDXLX2` | Stone & Beam Rug, 3'11" x 5'11", Blue, Navy, Multicolor | Amazon.com | CC-BY-4.0 | – | classic | -Y (low) | 5/4 | 1.78 x 1.18 x 0.0121 | x1 |
| rug | abo | `abo_B07HSF7LWP` | Stone & Beam Polypropylene Round Rug, 5'3" x 5'3", Gray, Orange, Multicolor | Amazon.com | CC-BY-4.0 | – | classic | -Y (low) | 5/5 | 1.6 x 1.6 x 0.0096 | x1 |
| rug | abo | `abo_B07TS7ZCVM` | Amazon Basics - 4'X6' Plush Diamond Trellis Shag Rug, Grey | Amazon.com | CC-BY-4.0 | – | neutral | -Y (low) | 5/4 | 1.78 x 1.22 x 0.03 | x1 |
| wall_art | abo | `abo_B073NZT572` | Amazon Brand – Stone & Beam Modern Print Wall Art of Brooklyn Bridge Sketch, Black Frame, 18" x 26" | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal | -Y (high) | 5/4 | 0.48 x 0.0155 x 0.657 | x1 |
| wall_art | abo | `abo_B073NZTB8J` | Amazon Brand – Stone & Beam Modern Red and Gold Tulip Print on Canvas, Brown Frame, 13.75" x 13.75" | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 5/4 | 0.349 x 0.0381 x 0.349 | x1 |
| wall_art | abo | `abo_B073P13J4L` | Amazon Brand – Rivet Aerial View Black, White and Gold Floral Canvas Print Wall Art, 16" x 16" | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 5/4 | 0.406 x 0.0415 x 0.406 | x1 |
| wall_art | abo | `abo_B073P13J54` | Amazon Brand – Rivet Patterned Color Circles Wall Art in White Frame, 26" x 38" | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 5/4 | 0.659 x 0.013 x 0.94 | x1 |
| wall_art | abo | `abo_B073P15SD2` | Amazon Brand – Stone & Beam Modern Gold Print of 1885 Baseball Bat Patent, Black Frame, 15" x 21" | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 5/4 | 0.374 x 0.0123 x 0.529 | x1 |
| wall_art | abo | `abo_B073P16J69` | Amazon Brand – Rivet World Map Hemisphere Print in Black and White Vintage Wall Art, Black Frame, 30.5" x 30.5" | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal | -Y (high) | 5/4 | 0.773 x 0.0313 x 0.775 | x1 |
| wall_art | abo | `abo_B073P19S7P` | Amazon Brand – Rivet Patterned Modern Pink and Grey Triangles in White Frame Wall Art, 18" x 26" | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 5/4 | 0.456 x 0.013 x 0.656 | x1 |
| wall_art | abo | `abo_B073P1BKT1` | Amazon Brand – Stone & Beam Modern Metallic Ink Reprint of Sailing Ship Patent Wall Art, Silver Frame, 15" x 21" | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 5/4 | 0.38 x 0.0132 x 0.533 | x1 |
| wall_art | abo | `abo_B073P1H7CF` | Black and White Vintage Bike Print in White Frame, 15" x 21" | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 5/4 | 0.332 x 0.0152 x 0.477 | x1 |
| wall_art | abo | `abo_B073P52NDX` | Amazon Brand – Stone & Beam Modern Black and White Desert Cactus Photo on Wood, White Frame, 20" x 20" | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal | -Y (high) | 5/4 | 0.508 x 0.0381 x 0.508 | x1 |
| wall_art | abo | `abo_B073P54PYL` | Amazon Brand – Rivet Modern Gold Pyramid Triangle Print Wall Art, 30" x 30", Black Frame | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.769 x 0.0416 x 0.766 | x1 |
| wall_art | abo | `abo_B073P5KYG9` | Amazon Brand – Stone & Beam Abstract Topographic Print in Black Wood Frame, 20" x 20" | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 5/4 | 0.507 x 0.0379 x 0.507 | x1 |
| wall_art | abo | `abo_B073P5L2QM` | Amazon Brand – Rivet Modern White Framed Black and White Paris Map Print, 30" x 30" | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal | -Y (high) | 5/4 | 0.758 x 0.0375 x 0.758 | x1 |
| wall_art | abo | `abo_B073P5MPW9` | Amazon Brand – Stone & Beam Modern Turquoise and Orange Palm Print in Gray Frame Wall Art, 12" x 12" | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/4 | 0.304 x 0.0377 x 0.303 | x1 |
| wall_art | abo | `abo_B073P6FYT4` | Amazon Brand – Rivet Vintage Blue Yellow and Green Chairs in Gold Wood Frame Wall Art, 20" x 20" | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 5/4 | 0.505 x 0.0371 x 0.505 | x1 |
| wall_art | abo | `abo_B075HWJ4K7` | Amazon Brand – Rivet Abstract Asian Influenced Grey and Black Print on Canvas Wall Art Decor, 36"W x 24"H | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 5/4 | 0.602 x 0.0482 x 0.916 | x1 |
| wall_art | abo | `abo_B07HSGM25V` | Amazon Brand – Stone & Beam Traditional Landscape Print with Copper Leaf Wall Art Decor on Canvas - 35" x 35" | Amazon.com | CC-BY-4.0 | – | neutral | -Y (high) | 4/4 | 0.888 x 0.0354 x 0.897 | x1 |
| vase | abo | `abo_B075HR4ZDB` | Amazon Brand – Stone & Beam Modern Decorative Ceramic Vase Decor With Geometric Pattern, 7.7 Inch Height, White | Amazon.com | CC-BY-4.0 | – | scandinavian, modern | -Y (low) | 5/5 | 0.159 x 0.159 x 0.2 | x1 |
| vase | abo | `abo_B075HWDSC6` | Amazon Brand – Rivet Rustic Stoneware Indoor Outdoor Flower Plant Home Decor Tall Cylinder Vase, 11"H, Silver | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (low) | 5/5 | 0.1 x 0.1 x 0.27 | x1 |
| vase | abo | `abo_B075HWDSZY` | Amazon Brand – Rivet Rustic Stoneware Indoor Outdoor Flower Plant Home Decor Tall Cylinder Vase, 11"H, Bronze | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (low) | 5/5 | 0.099 x 0.099 x 0.278 | x1 |
| vase | abo | `abo_B075HWDTHZ` | Amazon Brand – Rivet Rustic Stoneware Indoor Outdoor Flower Plant Home Decor Cylinder Vase, 9"H, Silver | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal | -Y (low) | 5/5 | 0.0454 x 0.0454 x 0.103 | x1 |
| vase | abo | `abo_B075HWX45W` | Amazon Brand – Rivet Rustic Stoneware Indoor Outdoor Flower Plant Home Decor Cylinder Vase, 9"H, Bronze | Amazon.com | CC-BY-4.0 | – | modern | -Y (low) | 5/5 | 0.1 x 0.1 x 0.227 | x1 |
| vase | abo | `abo_B078JFFX4L` | Amazon Brand – Stone & Beam Modern Round Ceramic Home Decor Flower Vase - 7 Inch, Coral White Tan | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (low) | 5/5 | 0.137 x 0.137 x 0.176 | x1 |
| vase | abo | `abo_B078JGHZT3` | Amazon Brand – Stone & Beam Modern Ceramic Home Decor Flower Vase - 7 Inch, Teal White Tan | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (low) | 5/5 | 0.116 x 0.116 x 0.179 | x1 |
| vase | abo | `abo_B078JGRLCJ` | Amazon Brand – Rivet Mid Century Modern Round Ceramic Home Decor Flower Vase - 5 Inch, Blue and Green | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (low) | 5/5 | 0.154 x 0.154 x 0.133 | x1 |
| vase | abo | `abo_B078JGYJTG` | Amazon Brand – Stone & Beam Modern Ceramic Home Decor Flower Vase - 11.75 Inch, Coral White Tan | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (low) | 5/5 | 0.144 x 0.144 x 0.296 | x1 |
| vase | abo | `abo_B078JJDPR2` | Amazon Brand – Stone & Beam Modern Ceramic Home Decor Flower Vase - 7 Inch, Teal White Tan | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (low) | 5/5 | 0.106 x 0.106 x 0.192 | x1 |
| vase | abo | `abo_B07HSLG6WR` | Amazon Brand – Rivet Westline Modern Indoor Outdoor Hand-Painted Stoneware Flower Vase, 9.5"H, Red White Blue Black | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (low) | 5/5 | 0.169 x 0.169 x 0.237 | x1 |
| vase | abo | `abo_B07JM1K8VH` | Amazon Brand – Rivet Westline Modern Indoor Outdoor Hand-Painted Stoneware Flower Vase, 9.5"H, Yellow White Blue Black | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (low) | 5/5 | 0.169 x 0.169 x 0.24 | x1 |
| vase | abo | `abo_B07QB8L3L5` | Amazon Brand – Stone & Beam Textured Modern Vase, 15.86"H, Blue | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (low) | 5/5 | 0.116 x 0.116 x 0.23 | x1 |
| vase | abo | `abo_B07QC8C7Y4` | Amazon Brand – Stone & Beam Textured Modern Vase, 12.4"H, White | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (low) | 5/5 | 0.202 x 0.202 x 0.335 | x1 |
| vase | abo | `abo_B07QC8CB15` | Amazon Brand – Stone & Beam Mid-Century Feather Vase, 8.66"H, Neutral and Gold | Amazon.com | CC-BY-4.0 | – | scandinavian, modern, neutral | -Y (low) | 5/5 | 0.172 x 0.172 x 0.27 | x1 |
| vase | abo | `abo_B07QC8CFCY` | Amazon Brand – Ravenna Home Mid-Century Stoneware Vases, Set of 3, 4.8"H, 3 colors | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (low) | 5/5 | 0.297 x 0.0975 x 0.122 | x1 |
| vase | abo | `abo_B07QD6ZC1P` | Amazon Brand – Stone & Beam Modern Stoneware Vase, 10.51"H, Blue and Sand | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (low) | 5/5 | 0.163 x 0.163 x 0.267 | x1 |
| vase | abo | `abo_B07QD6ZV84` | Amazon Brand – Stone & Beam Mid-Century Rustic Vase, 8.66"H, Neutral | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (low) | 5/5 | 0.172 x 0.172 x 0.27 | x1 |
| vase | abo | `abo_B07QFB5MW6` | Amazon Brand – Stone & Beam Textured Modern Vase, 9.05"H, Gray | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern, neutral | -Y (low) | 5/5 | 0.297 x 0.297 x 0.499 | x1 |
| vase | abo | `abo_B07QFB5MXX` | Amazon Brand – Rivet Mid-Century Metallic Stoneware Vase, 11.8"H, Gold | Amazon.com | CC-BY-4.0 | – | japandi, neutral | -Y (low) | 5/5 | 0.061 x 0.0612 x 0.143 | x1 |
| bowl | generated | `gen_bowl_industrial_1_8fc4b9a1` | Generated industrial bowl (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal, industrial, neutral | -Y (low) | 5/5 | 0.35 x 0.35 x 0.174 | x0.348778 |
| bowl | generated | `gen_bowl_japandi_1_6596ba4b` | Generated japandi bowl (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (low) | 5/5 | 0.35 x 0.35 x 0.107 | x0.348813 |
| bowl | generated | `gen_bowl_mediterranean_1_80ad0595` | Generated mediterranean bowl (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | scandinavian, japandi, minimal, modern, neutral | -Y (low) | 5/5 | 0.35 x 0.35 x 0.111 | x0.349839 |
| bowl | generated | `gen_bowl_minimal_1_58d9a7aa` | Generated minimal bowl (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | scandinavian, modern minimal, minimal, modern | -Y (low) | 5/5 | 0.35 x 0.35 x 0.125 | x0.348845 |
| bowl | generated | `gen_bowl_modern_1_c5302d78` | Generated modern bowl (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern | -Y (low) | 5/5 | 0.351 x 0.349 x 0.127 | x0.349432 |
| bowl | generated | `gen_bowl_modern_minimal_1_8e554715` | Generated modern minimal bowl (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | modern minimal, minimal | -Y (low) | 5/4 | 0.35 x 0.35 x 0.1 | x0.348926 |
| bowl | generated | `gen_bowl_rustic_1_4d403b64` | Generated rustic bowl (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | industrial, rustic | -Y (low) | 4/5 | 0.35 x 0.35 x 0.0965 | x0.349347 |
| bowl | generated | `gen_bowl_scandinavian_1_ca5c9c50` | Generated scandinavian bowl (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | scandinavian, modern minimal, minimal, modern | -Y (low) | 5/5 | 0.35 x 0.35 x 0.0976 | x0.348841 |
| bowl | generated | `gen_bowl_scandinavian_2_10f5db00` | Generated scandinavian bowl (2) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | scandinavian, modern minimal, minimal, modern | -Y (low) | 5/5 | 0.35 x 0.35 x 0.109 | x0.348887 |
| plant_small | generated | `gen_plant_small_classic_1_08e9f778` | Generated classic plant small (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | scandinavian, japandi, modern minimal, minimal, modern, neutral | -Y (low) | 5/5 | 0.297 x 0.264 x 0.365 | x0.364209 |
| plant_small | generated | `gen_plant_small_industrial_1_94d74431` | Generated industrial plant small (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | scandinavian, japandi, modern minimal, minimal, modern, neutral | -Y (low) | 5/5 | 0.257 x 0.305 x 0.368 | x0.367121 |
| plant_small | generated | `gen_plant_small_japandi_1_32d3b9fb` | Generated japandi plant small (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (low) | 5/5 | 0.285 x 0.276 x 0.356 | x0.355152 |
| plant_small | generated | `gen_plant_small_mediterranean_1_3691e399` | Generated mediterranean plant small (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | scandinavian, japandi, modern minimal, minimal, modern, mediterranean, neutral | -Y (low) | 5/5 | 0.273 x 0.287 x 0.323 | x0.321704 |
| plant_small | generated | `gen_plant_small_minimal_1_6f2e772d` | Generated minimal plant small (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | scandinavian, modern minimal, minimal, modern | -Y (low) | 5/5 | 0.284 x 0.276 x 0.37 | x0.368961 |
| plant_small | generated | `gen_plant_small_modern_1_e1ff6032` | Generated modern plant small (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | scandinavian, japandi, modern minimal, minimal, modern, neutral | -Y (low) | 5/5 | 0.291 x 0.269 x 0.335 | x0.333959 |
| plant_small | generated | `gen_plant_small_modern_minimal_1_7ea34d3d` | Generated modern minimal plant small (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | scandinavian, japandi, modern minimal, minimal, modern, neutral | -Y (low) | 5/5 | 0.273 x 0.287 x 0.33 | x0.328613 |
| plant_small | generated | `gen_plant_small_rustic_1_5cdaa51b` | Generated rustic plant small (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | scandinavian, japandi, modern minimal, minimal, modern, neutral | -Y (low) | 5/5 | 0.292 x 0.268 x 0.4 | x0.399113 |
| plant_small | generated | `gen_plant_small_scandinavian_1_0dcfdd60` | Generated scandinavian plant small (1) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | scandinavian, modern minimal, minimal, modern | -Y (low) | 5/5 | 0.274 x 0.286 x 0.345 | x0.343999 |
| plant_small | generated | `gen_plant_small_scandinavian_2_20075b95` | Generated scandinavian plant small (2) | generated: TRELLIS.2-4B (Microsoft, MIT) from a Z-Image-Turbo image | generated (TRELLIS.2-4B, MIT) | – | scandinavian, modern minimal, minimal, modern | -Y (low) | 5/5 | 0.265 x 0.295 x 0.342 | x0.341281 |
| table_lamp | abo | `abo_B07374P6MR` | Amazon Brand – Stone & Beam Modern Bedroom Table Desk Lamp With Light Bulb - 8 x 8 x 20.5 Inches, Wood Grain | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (low) | 5/5 | 0.244 x 0.244 x 0.536 | x1 |
| table_lamp | abo | `abo_B07374QFJ3` | Amazon Brand – Stone & Beam Glass Column Living Room Table Desk Lamp With Light Bulb and Linen Shade, 23"H, Black | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (low) | 4/4 | 0.211 x 0.211 x 0.509 | x1 |
| table_lamp | abo | `abo_B07374VCVN` | Amazon Brand – Rivet Copper Geometric Bedside Table Desk Lamp With Light Bulb - 16.75 Inches, Copper | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (low) | 4/4 | 0.3 x 0.3 x 0.431 | x1 |
| table_lamp | abo | `abo_B073P3HHFS` | Rivet Pike Factory Industrial Table Lamp With Light Bulb - 6 x 13 x 19 Inches, Brushed Steel | Amazon.com | CC-BY-4.0 | – | industrial | -Y (low) | 4/4 | 0.286 x 0.153 x 0.456 | x1 |
| table_lamp | abo | `abo_B075X12QV5` | Rivet Mid Century Modern Rubberwood Living Room Table Lamp With Light Bulb - 19 Inches, Black with Linen White Shade | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (low) | 4/4 | 0.241 x 0.24 x 0.482 | x1 |
| table_lamp | abo | `abo_B075X2FW6F` | Rivet Wood and Black Marble Lamp, Mid-Century Walnut, With Bulb, 18"H | Amazon.com | CC-BY-4.0 | – | neutral | -Y (low) | 4/4 | 0.202 x 0.202 x 0.349 | x1 |
| table_lamp | abo | `abo_B075X2NLK5` | Rivet Modern Deer Head Ceramic Lamp With Bulb, 19.5"H, White and Brass | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (low) | 4/4 | 0.298 x 0.298 x 0.503 | x1 |
| table_lamp | abo | `abo_B07B4VGZ9B` | Amazon Brand – Rivet Mid-Century Modern Curved Task Desk Table Lamp With USB Port And Light Bulb - 26 Inches, Matte Black &amp; Brushed Steel | Amazon.com | CC-BY-4.0 | – | modern, industrial | -Y (low) | 5/4 | 0.189 x 0.292 x 0.646 | x1 |
| table_lamp | abo | `abo_B07DBDV67C` | Amazon Brand – Ravenna Home Accent Table Lamp with LED Light Bulb -18.5 Inches, Brushed Nickel with White Shade | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (low) | 4/4 | 0.328 x 0.328 x 0.619 | x1 |
| table_lamp | abo | `abo_B07DT4GY4W` | Amazon Brand – Stone & Beam Modern Farmhouse Wood Cylinder Table Desk Lamp With LED Light Bulb And White Shade- 14 x 14 x 27 Inches | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (low) | 4/4 | 0.348 x 0.348 x 0.667 | x1 |
| table_lamp | abo | `abo_B07HK3PNSK` | Rivet Contemporary Palm Tree Neon Table Lamp, 11.75"H, White AF44228 | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (low) | 4/4 | 0.168 x 0.0885 x 0.317 | x1 |
| table_lamp | abo | `abo_B07HK8YHB7` | Amazon Brand – Rivet Mid-Century Modern Cone Nightstand Table Desk Lamp with LED Light Bulb - 15 Inches, Black and Gold | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (low) | 4/4 | 0.308 x 0.308 x 0.58 | x1 |
| table_lamp | abo | `abo_B07HKGHSR7` | Amazon Brand – Rivet Modern Two Tone Table Desk Lamp with LED Light Bulb and Drum Shade - 12 x 12 x 15.88 Inches, Matte Black and Antique Brass | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (low) | 4/4 | 0.304 x 0.304 x 0.573 | x1 |
| table_lamp | abo | `abo_B07MBFD6F9` | Amazon Brand – Ravenna Home Metal Table Lamp with LED Light Bulb, 20"H, Dark Bronze | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal | -Y (low) | 4/4 | 0.251 x 0.251 x 0.509 | x1 |
| table_lamp | abo | `abo_B07MF1RNW1` | Amazon Brand – Ravenna Home Classic Straight Banker's Task Desk Lamp with LED Light Bulb, 16"H, Brushed Nickel | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (low) | 5/4 | 0.269 x 0.227 x 0.404 | x1 |
| table_lamp | abo | `abo_B07MF1S4SK` | Amazon Brand – Ravenna Home Round Base Table Lamp with LED Light Bulb, 20"H, Dark Bronze | Amazon.com | CC-BY-4.0 | – | industrial | -Y (low) | 4/4 | 0.286 x 0.286 x 0.51 | x1 |
| table_lamp | abo | `abo_B07MHMNK1L` | Amazon Brand – Stone & Beam Two-Toned Ceramic Base Table Lamp, Bulb Included, 19.75"H, Beige | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal | -Y (low) | 4/4 | 0.212 x 0.212 x 0.493 | x1 |
| table_lamp | abo | `abo_B0824F6HZ4` | Amazon Brand – Ravenna Home Traditional Metal Downbridge Desk Lamp with Adjustable Shade, LED Bulb Included, 19.25"H, Brushed Nickel | Amazon.com | CC-BY-4.0 | – | modern | -Y (low) | 5/4 | 0.171 x 0.333 x 0.488 | x1 |
| table_lamp | abo | `abo_B0825CP3NS` | Amazon Brand – Rivet Scandinavian Real Blond-Wood Table Lamp with Marble Bottom, LED Bulb Included, 18.5"H, Beige | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (low) | 4/4 | 0.229 x 0.229 x 0.47 | x1 |
| table_lamp | abo | `abo_B0825CXG81` | Amazon Brand – Rivet Scandinavian Real Wood Table Lamp with Faux Marble Base, LED Bulb Included, 17.5"H, Gray Wood | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal | -Y (low) | 4/4 | 0.228 x 0.228 x 0.444 | x1 |
| mirror | abo | `abo_B0713T6T4D` | Amazon Brand – Stone & Beam Iron Latticework Decorative Hanging Mirror Wall Art, 39.4 Inch Height, Verdi Green | Amazon.com | CC-BY-4.0 | – | modern | -Y (high) | 4/4 | 0.767 x 0.0297 x 0.983 | x1 |
| mirror | abo | `abo_B0718ZKQK8` | Amazon Brand – Stone & Beam Rustic Wood and Rope Geo Mirror, 36" H, Natural | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern, neutral | -Y (high) | 5/4 | 0.606 x 0.0436 x 0.912 | x1 |
| mirror | abo | `abo_B071HBBDZ1` | Amazon Brand – Stone & Beam Round Wood Quadrant Hanging Wall Mirror, 15 Inch Height, Dark Wood Finish | Amazon.com | CC-BY-4.0 | – | japandi, neutral | -Y (high) | 5/4 | 0.382 x 0.02 x 0.381 | x1 |
| mirror | abo | `abo_B071V8LJQJ` | Amazon Brand – Stone & Beam Square Wood Quadrant Hanging Wall Mirror, 15 Inch Height, Dark Wood Finish | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 5/4 | 0.382 x 0.0197 x 0.381 | x1 |
| mirror | abo | `abo_B071V8M937` | Amazon Brand – Stone & Beam Sunburst Lines Hanging Wall Mirror Decor, 20 Inch Height, Antique Gold Finish | Amazon.com | CC-BY-4.0 | – | modern, neutral | -Y (high) | 5/4 | 0.509 x 0.0424 x 0.507 | x1 |
| mirror | abo | `abo_B07B4W5R8N` | Amazon Brand – Rivet Jonathan Mid-Century Modern Mirror Wood Frame, 52", Walnut | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/4 | 1.33 x 0.0448 x 1.02 | x1 |
| mirror | abo | `abo_B07B8NW6GG` | Amazon Brand – Stone & Beam Rustic Farmhouse Round Wood Iron Mirror with Faux Leather Strap - 22 Inch, Black Metal | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, neutral | -Y (high) | 4/4 | 0.355 x 0.0423 x 0.568 | x1 |
| mirror | abo | `abo_B07RNMMYNR` | Amazon Basics Rectangular Wall Mirror 16" x 20" - Peaked Trim, White | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 5/4 | 0.406 x 0.0406 x 0.509 | x1 |
| mirror | abo | `abo_B07RNMMYPR` | Amazon Basics Rectangular Wall Mirror 30" x 40" - Peaked Trim, White | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 5/4 | 0.762 x 0.0406 x 1.02 | x1 |
| mirror | abo | `abo_B07RNMNFQ5` | Amazon Basics Rectangular Wall Mirror 30" x 40" - Standard Trim, Walnut | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/4 | 0.762 x 0.0402 x 1.02 | x1 |
| mirror | abo | `abo_B07RNMNGYF` | Amazon Basics Rectangular Wall Mirror 24" x 36" - Standard Trim, Black | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 5/4 | 0.609 x 0.0402 x 0.915 | x1 |
| mirror | abo | `abo_B084DQ9VWM` | Amazon Brand – Ravenna Home Vintage Wooden Accent Mirror, 27.75"H, Natural | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, minimal, modern | -Y (high) | 5/4 | 0.686 x 0.019 x 0.686 | x1 |
| mirror | abo | `abo_B084HTY39G` | Amazon Brand - Rivet Modern Rhombus Cutout Hanging Mirror, 26.75"H, Gold | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 5/4 | 0.419 x 0.0317 x 0.679 | x1 |
| mirror | abo | `abo_B084HTZ2C6` | Amazon Brand - Rivet Modern Round Hanging Mirror with Shelf, 18" Diameter, Gold | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/5 | 0.457 x 0.133 x 0.457 | x1 |
| mirror | abo | `abo_B084HV148L` | Amazon Brand - Rivet Modern Round Cutout Hanging Mirror, 22.25" Diameter, Gold | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 5/4 | 0.565 x 0.0318 x 0.565 | x1 |
| mirror | abo | `abo_B084HV5LK3` | Amazon Brand - Rivet Modern Oval Hanging Mirror, 39"H, Gold | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/4 | 0.222 x 0.0318 x 0.991 | x1 |
| mirror | abo | `abo_B084HV67GW` | Amazon Brand - Rivet Modern Cutout Hanging Mirror, 23"H, Gold | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/4 | 0.584 x 0.0317 x 0.254 | x1 |

## Attribution

Contains information from Objaverse 1.0 (https://huggingface.co/datasets/allenai/objaverse, revision 21e4e14), which is made available under the ODC Attribution License (ODC-By 1.0, https://opendatacommons.org/licenses/by/1-0/). Every object keeps its own licence, as declared by its uploader and not verified by WenArt_RUN (CC0 1.0 and CC BY 4.0 unflagged, every other licence flagged: docs/milestone8.md §2): check it before commercial use. This file is licensed ODC-By 1.0, not MIT.

Contains 3D models and product data from Amazon Berkeley Objects (https://amazon-berkeley-objects.s3.amazonaws.com/index.html), (c) Amazon.com, licensed CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Credit for the data, including all images and 3D models: Amazon.com; for building the dataset: Matthieu Guillaumin, Thomas Dideriksen, Kenan Deng, Himanshu Arora (Amazon.com), Jasmine Collins and Jitendra Malik (UC Berkeley). Changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched.

Generated models (docs/milestone8.md §3): made by TRELLIS.2-4B (microsoft/TRELLIS.2-4B, MIT) from Z-Image-Turbo product images; marked `generated`, no third-party credit.

- "Amazon Brand - Movian Aveyron Single Bed Frame, 195 x 100 x 80cm, Pink" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "AmazonBasics Foldable, 14" Metal Platform Bed Frame with Tool-Free Assembly, No Box Spring Needed - Twin" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "AmazonBasics Faux Leather Upholstered Platform Bed Frame with Wooden Slats, Twin" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Movian Moselle." by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Movian Moselle." by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Modern Solid Pine Wood Platform Bed, Twin, 38.39"W, Antique Espresso" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "AmazonBasics Metal Bed with Modern Industrial Design Headboard - 14 Inch Height for Under-Bed Storage - Wood Slats - Easy Assemble, Twin" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Generated classic bed single (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated industrial bed single (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated japandi bed single (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated mediterranean bed single (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated mediterranean bed single (2)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated minimal bed single (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated modern bed single (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated modern minimal bed single (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated rustic bed single (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated scandinavian bed single (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Lowpoly Bed" by Mohamed199 (https://sketchfab.com/3d-models/6eb4212e70b941a3bd2db196a47828b9), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Bed - Sample" by Mifu Saja (https://sketchfab.com/3d-models/b547d81073b64d3e97200fd3ae9a74af), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian Loue Bed Frame with Headboard, 160 x 200cm, White/Light Brown Oak-Effect" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Movian Belaya" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Intex Premaire Luchtbed met Fiber Tech-technologie, nieuwe geïntegreerde elektrische pomp met gegevens en USB, PVC, grijs, 152 x 203 x 46 cm" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Glenwood Industrial Metal Accent Bed, Queen, 84.5"L, Oak" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Glenwood Industrial Metal Accent Bed, King, 86"L, Oak" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Ventura Mid-Century Louvered Queen Bed, 86"L, Cherry" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Payton Mid-Century Modern Tufted King Bed with Headboard, 82" W, Natural" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Bateman Casual Rustic Wood Platform Bed Frame with Tall Headboard, King, 81"W, Brown" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Tisbury Nailhead Trim Queen Bed, 66"W, Fresh Pewter" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Stone & Beam Prudence Tufted King Bed, 84"W, Spinnsol Cocoa" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian Corona Double Bed, 4 ft 6, High Foot End Bed Frame, Solid Pine Wood" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Movian Havel" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian Constance Lift-Up Double Bed Frame with Storage, 190 x 140 x 31.5cm, Light Brown Oak-Effect" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Solimo Aquilla Engineered Wood Queen Bed (Wenge Finish)" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Rustic Solid Pine Bed with Headboard, King, 81.89"W, Gray" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Rustic Solid Pine Platform Bed, Queen, 63.15"W, Gray" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "AmazonBasics Solid Platform Bed - Rustic Finish - No Box Spring Needed - Strong Wood Slat Support, Queen" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Solimo Senna Metal Glossy King Bed (Black)" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Bed" by Ambriel (https://sketchfab.com/3d-models/08f7f65edfea417b8ed9ca748381e507), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Old Bed" by barism09 (https://sketchfab.com/3d-models/5d3a99865ac84d8a8bf06b263aa5bb55), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Bradbury Chesterfield Tufted Leather Sofa Couch, 92.9"W, Cognac" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Hoffman Down-Filled Performance Fabric Loveseat Sofa, 79"W, Ecru" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Bradbury Chesterfield Tufted Sofa Couch, 92.9"W, Hemp" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Marchio Amazon - Movian Ackan - Divano a 3 posti, 209 x 87 x 80 cm, grigio chiaro" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Bradbury Chesterfield Tufted Loveseat Sofa Couch, 78.7"W, Navy" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Aiden Tufted Mid-Century Leather Bench Seat Sofa, Without Side Pillows, 74"W, Cognac" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Uptown Mid-Century Velvet Tufted Customizable Daybed Sofa, 78"W, Dove Grey &amp; Brass" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Eva Tufted Mid-Century Velvet Down-Filled Loveseat, 60.5"W, Hunter Green" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Andover Studio Sofa Couch, 78"W, Driftwood Leather" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Bradbury Chesterfield Tufted Leather Loveseat Sofa Couch, 78.7"W, Black" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Bagley Sectional Component, Left-Facing Loveseat, Fabric, 52"W, Linen" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Bagley Sectional Component, Right Facing Loveseat, Fabric, 52"W, Linen" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Bagley Sectional Component, Armless Loveseat, Fabric, 44"W, Linen" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Bagley Sectional Component, Left-Facing Sofa Chaise, Fabric, 41"W, Linen" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Bagley Sectional Component, Right-Facing Sofa, Fabric, 75"W, Linen" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian Dyvran 3-Seater Upholstered Sofa, 197 x 83 x 83 cm, Stain-Resistant Polyester, Dust Blue" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian Keitele - 2 Seater Sofa, 130 x 82 x 84, Light Grey" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Generated japandi sofa (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated japandi sofa (2)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Sofa" by hask191919 (https://sketchfab.com/3d-models/104ac40ef3ad4dac8079a11548c470e7), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Huxley Mid-Century Modern Accent Chair, 28.3"W, Marine Blue" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Emerly Modern Living Room Chair, 41"W, Pewter" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Farr Lotus Accent Chair, Felt Grey" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Emerly Modern Living Room Chair, 41"W, Ecru" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Highland Modern Wingback Living Room Accent Chair, 31.9"W, Oatmeal" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Charlotte Mid-Century Modern Upholstered Gold Accent Chair, 29"W, Natural" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand Movian Dofsan Chair 100 x 93 x 86 cm Grey" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Curved Tufted Velvet Accent Chair, Marina Mid-Century, 28.7"W, Hunter Green" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Hillsboro Modern Wingback Living Room Accent Chair With Nailhead Trim, 29"W, Beige" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Aiden Tufted Mid-Century Modern Velvet Accent Chair, 35.4"W, Otter Grey" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Villain Mid-Century Modern Leather Metal Leg Accent Lounge Chair, 37.4"W, Black" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Aubree Farmhouse Accent Arm Chair, 32"W, Striped Red Linen" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Ravenna Home Hughes Curved Back Tufted Patterned Accent Chair, 25"W, Arrow" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Calhoun Living Room Accent Chair, 42"W, Ecru" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "animated_sphere" by ferhatsen (https://sketchfab.com/3d-models/124297e7e4574c48b9c1b814b6ddf516), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Lpuvw" by juliaowoc (https://sketchfab.com/3d-models/5b9e8ba19b1b454f82898ac4809f02b2), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Oldfashioned armchair" by yezzyx (https://sketchfab.com/3d-models/69f1c0489a144f3c98e66dcfe72b3969), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Chair_2 out of 12" by 3Dtrickster (https://sketchfab.com/3d-models/a07501cd7f6c40fc9cf4cf438e41bac1), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "High back Arm chair (Free Download)" by dopaminecat (https://sketchfab.com/3d-models/b23ec9725c48494788d1d88104acbb4a), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "LPUVW" by HannaPachurka (https://sketchfab.com/3d-models/da6d646358d1451fa751f1a9141290a3), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Mid-Century Modern Oak Dining Table, 63"L, Walnut Finish" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Industrial Mid-Century Modern Hairpin Dining Table, 70.9"L, Walnut and Black" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Industrial Wood and Metal Round Dining Kitchen Table, 35.4"W, Recycled Elm" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Dunbar Wood Dining Room Kitchen Table, 78"L, Oak Finish" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Alejandra Casual Wood Dining Kitchen Table, 78"-98"L, Brown" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Bradhurst Casual Farmhouse Wood Dining Kitchen Table, 61"-84"L, White" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Ian Modern Medium Dining Kitchen Table, Expandable, 60-80"L, Brown" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Mid-Century Modern Wood Round Dining Kitchen Table, 43.3"W, Beige" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Movian Moselle Dining Table, 160 x 76 x 90cm, Oak Sonoma Colour" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian Kuban Dining Table, 160 x 78 x 90cm, Brown Oak-Effect Table Top/Black Legs" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Alkove Hayes Solid Wood Dining Table with Stainless Steel Base, Seats 6, 180 x 90 x 75cm, Wild Oak/Stainless Steel" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Ravenna Home Traditional Dining Table 29"H, Gray and Rustic Honey Pine" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Ravenna Home Traditional Dining Table 29"H, Black and Rustic Honey Pine" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Fulton Modern Rustic Dining Table, 71"L, Natural" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand Movian Kyyvesi Dining Table 120.5 x 71.4 x 76 cm Walnut Effect" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Alkove Hayes Classic Fixed Solid Wood Dining Table, Seats 4-6, 130 x 90 x 75cm, Wild Oak" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian Kyyvesi, Dining Table, 180 x 90 x 75 cm, Oak Effect" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Mid-Century Modern Pine Extendable Dining Table, 39"–77"W, Brown" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Dining Set" by dan2211082 (https://sketchfab.com/3d-models/3b4ee19c627e4fb4a3305621cf925aa2), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "A table, chairs & few cups" by Sahramin (https://sketchfab.com/3d-models/724d93a7f3644f96909e8c55909c6418), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Alkove Waverly Large Coffee Table with Shelf in Light Oak Finish" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Industrial Modern Wood and Metal Coffee Table, 31.5"W, Walnut" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Allyson Mid-Century Modern Two-Shelf Adjustable Coffee Table, Walnut" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Modern Round Glass and Gold Coffee Table, 36"W, Gold Finish" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Hillside Antiqued Round Coffee Table, 39.4"D, Wood and Bronze" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Larson Industrial Wood & Metal Coffee Table, 50"W, Walnut" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Ravenna Home Parker Coffee Table, 47.2"W, Marble &amp; Gold" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Rivet Leaf-Shaped Coffee Table, 120 x 60 x 36cm, MDF with Walnut Veneer/Black Metal Base" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Rivet Round Coffee Table with Solid Wood Legs, 80 x 80 x 36cm, MDF with Walnut Veneer/Solid Beech Wood" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Rivet Triangular Coffee Table with Solid Wood Legs, 105 x 60 x 37cm, MDF with Walnut Veneer/Solid Beech Wood" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "ROCKPOINT Argus Lift-Top Wood Coffee Table, Sandy Oak" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Phoenix Home Rustic Industrial Solid Wood and Steel Open Shelf Coffee Table, Brown" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Industrial Coffee Table, 53"W, Antique Natural and Black" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Ryder Industrial Round Coffee Table, 43.3" Diameter, Brushed Natural Antique Copper" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Solimo Veronica Engineered Wood Coffee Table (Espresso Finish)" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Palette Table" by Javier.Cantero (https://sketchfab.com/3d-models/01ff88bfc0034211b9f4996d620bc333), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "55555" by Gulin (https://sketchfab.com/3d-models/956a47ccc1a54a40a8711f3852d54433), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "MESA COMEDOR" by Fer.Arq (https://sketchfab.com/3d-models/bbe1d47c0d714884a66c53d6c1e5d177), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Modern Table" by Athlas (https://sketchfab.com/3d-models/c17577daa87849d09960669606c0ce27), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "LP Table" by doplerato (https://sketchfab.com/3d-models/f4031bb5f7e64ebca4c37d4fa5ba6e8d), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian Haven Retro Desk with Riser, Grey Oak, 113.54 x 60.45 x 89.92 cm" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Marchio Amazon - Movian Scrivania Candon, Marrone medio, 114,3 x 49,53 x 76,454 cm" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Mid-Century Curved Wood Table Home Office Computer Desk, 48.4"L, Walnut" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Industrial Metal Office Computer Desk, 60"W, Power Sit to Standing Table, Brown/Black" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Anne Farmhouse French Wood Desk, 62"W, Blue" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Rivet Mid-Century Home Office Computer Desk with 1 Drawer & Curved Corners, 57 x 123 x 79cm, White/MDF with Walnut Veneer" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian Idro 3-Drawer Desk, 56 x 110 x 73.5cm, Light Brown/Oak Foil Finish" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian Idro 4-Drawer Desk, 56 x 110 x 73cm, Light Brown/Oak Foil Finish" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian Indre 1-Drawer Desk, 56 x 110 x 73cm, Light Brown/Oak Foil Finish" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Mid-Century Desk - 35 Inch, Natural" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian Stanberg 1-Door 1-Drawer Writing Desk, 140 x 55 x 76cm, Light Brown Oak-Effect/Black" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "AmazonBasics Classic, Home Office Computer Desk With Shelves, Black" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "AmazonBasics Foldable Standing Computer Desk with Storage Shelf, Adjustable Height, Easy Assembly - Black" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "AmazonBasics Gaming Computer Desk with Storage for Controller, Headphone & Speaker - Red" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand-Movian Ljungan Desk, 114 x 60 x 90cm, Dark Brown/Black" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian Côa 4-Drawer Desk, 160 x 73 x 77.5cm, Vintage Dark Brown Oak-Effect/Black Metal" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Avery Industrial Home Office Writing Desk with Metal Base, 40"W, Chestnut Brown Finish" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "AmazonBasics 40" Multipurpose Foldable Computer Study Desk - Natural" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "FF Desk Drawer 3D Test 5 Obj" by fabcreative (https://sketchfab.com/3d-models/1b256f6ce7924f59a756fe8f7ba69416), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Table Colored DZ" by slayer11 (https://sketchfab.com/3d-models/b05862a2023f4c02988b3bb3004f6ff6), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "AmazonBasics Sedia direzionale da ufficio con schienale alto, regolabile in altezza - Marrone" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Ashworth Armless Velvet Accent Chair, 21.6"W, Navy" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Federal Mid-Century Modern Wood Dining Room Kitchen Chairs, 36 Inch Height, Set of 2, Black" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Ravenna Home Armless Tufted Turned Wood Leg Accent Chair, 29"W, Blue" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Ravenna Home Tufted Armless English Roll Traditional Accent Chair, 26.8"W, Merlot Red" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Phoenix Home PU Leather Dining Chair Set of 2, 18.11" Length x 21.65" Width x 30.7" Height, Brown" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian Square" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Alkove - Hayes - Modern Solid Wood Chairs Set of 2 with Padded Seat - Wild Oak" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Ravenna Home Dining Chairs, Set of 2, 40"H, Praline" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Erikson Vegan Leather Woven Dining Chair, Set of 2, 18"W, Beige" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Vivianne Modern Upholstered Armless Dining Chair with Casters, 19.7"W, Slate" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Modern Farmhouse Birch Dining Chair, 17.5"W, Dark Gray" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Mid-Century Beech and Rattan Dining Chair with Arms, 21.9"W, Natural" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Rocking Chair" by Christian (https://sketchfab.com/3d-models/039c6026571943d6ac45c6816bcc7ff1), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Old chair" by Dani Ortega (https://sketchfab.com/3d-models/0723b35415b0462eb5c01140b6b70340), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Wicker Chair" by Scott Thorne (https://sketchfab.com/3d-models/1625701880c54b7d9f50e77455cef39b), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Char 2" by DimaSP (https://sketchfab.com/3d-models/47a690dcecf847fca99c4f89111db85b), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "chare" by DimaSP (https://sketchfab.com/3d-models/acf6497a3d274d90ad3750510348f07a), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Vintage Chair" by Maycho (https://sketchfab.com/3d-models/cb43e2abac66494d81e1e7116eb47043), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Chair" by 杭州维界科技有限公司 (https://sketchfab.com/3d-models/d2785b57e7da45858f2fe8bf4dedd68d), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Vida Designs Corona Wardrobe, 3 Door, Solid Pine Wood, Solid Pine Wood, Distressed Waxed Pine Bedroom Wooden Storage Mexican Furniture" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian Inari Modern 2-Door 2-Drawer Wardrobe, 100 x 57 x 180 cm, Light Brown Oak-Effect" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian Indre 3-Door 3-Drawer Wardrobe, 129 x 51 x 191cm, Dark Grey" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian Kolva Sliding 2-Door Wardrobe, 180 x 61 x 197cm, Light Brown Oak-Effect" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian Inari Modern 2-Door 2-Drawer Wardrobe, 100 x 57 x 180 cm, Dark Grey" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian Kolva Sliding 2-Door Wardrobe, 180 x 61 x 197cm, Dark Grey" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian Morava 4-Door 2-Drawer Wardrobe with Mirrors, 200 x 59 x 212cm, Light Brown Oak-Effect" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian Cinca 5-Door Wardrobe with Mirrors and Internal Storage Compartments, 226 x 216 x 62cm, White/Oak-Colour Accents" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian Moselle 2-Door Wardrobe, 100 x 60 x 196 cm, Light Brown Oak-Effect/White" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian Mira 4-Door Wardrobe with Mirrors, 181 x 207 x 58cm, Light Brown Oak-Effect" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Generated classic wardrobe (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated industrial wardrobe (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated rustic wardrobe (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated scandinavian wardrobe (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Dikkies Closet" by klaxoneer (https://sketchfab.com/3d-models/05a035c3347645b8a7ceb6d65f825ac3), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Wardrobe" by Kevin98 (https://sketchfab.com/3d-models/08a3baeb2e0847939d53027824de5a49), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Traditional Mennonite corner cabinet" by vinigor (https://sketchfab.com/3d-models/094697a23146463cb5564ac8bf89e5c4), CC BY-NC 4.0 (https://creativecommons.org/licenses/by-nc/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (licence flag: non_commercial)
- "Cabinet" by trijoko.maryadi (https://sketchfab.com/3d-models/6d443f619ecd404a81769c70f447ba86), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Warn Wardrobe" by seenoise (https://sketchfab.com/3d-models/b3a99e956be64ab6958f7f5e1895f031), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Simple Tall Shelf" by Blender3D (https://sketchfab.com/3d-models/b46803ba0bc64e12b31f832fb761c4e0), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Generated industrial fridge (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated japandi fridge (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated japandi fridge (2)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated japandi fridge (3)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated mediterranean fridge (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated modern minimal fridge (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated rustic fridge (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated scandinavian fridge (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Refrigerator - Grey Polished Metal" by Glowbox 3D (https://sketchfab.com/3d-models/2071bda681b642218b6829b82e4fd93b), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Fridge" by Yaseen Ali (https://sketchfab.com/3d-models/66878d980a364b2db1a5cc44c67bb45d), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Old Fridge" by golddog (https://sketchfab.com/3d-models/68d69bbf7a454a09a2536ac0762532f3), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Haier Refrigerator" by cgwings (https://sketchfab.com/3d-models/c9c4e705bf794cb88d5d8726095f4917), CC BY-NC 4.0 (https://creativecommons.org/licenses/by-nc/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (licence flag: non_commercial)
- "Stylized Fridge" by sauti (https://sketchfab.com/3d-models/f32ec9229a8749d1b79245813fbd6c31), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Generated classic stove (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated industrial stove (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated japandi stove (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated modern stove (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated modern minimal stove (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated rustic stove (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated scandinavian stove (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated scandinavian stove (2)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Stove from Poly by Google" by IronEqual (https://sketchfab.com/3d-models/68e164f1a9414c29820ac2eaf6d8ac04), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Stove" by Daniyal Malik (https://sketchfab.com/3d-models/7c5c9dec5c2e4ff998c386410b0e3686), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "R RETRO FIRIN" by Motto Teknoloji (https://sketchfab.com/3d-models/934716ccd00d4f6ba9555d1cea788488), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Generated japandi sink kitchen (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated japandi sink kitchen (2)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated japandi sink kitchen (3)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated japandi sink kitchen (4)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated mediterranean sink kitchen (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated modern sink kitchen (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated modern sink kitchen (2)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated rustic sink kitchen (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated scandinavian sink kitchen (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated scandinavian sink kitchen (2)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated scandinavian sink kitchen (3)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated classic washbasin (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated industrial washbasin (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated japandi washbasin (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated japandi washbasin (2)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated japandi washbasin (3)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated mediterranean washbasin (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated minimal washbasin (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated modern washbasin (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated modern minimal washbasin (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated rustic washbasin (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated scandinavian washbasin (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Combo CEG-50BF" by Stala (https://sketchfab.com/3d-models/295384601e0d4f1985a919253330d59d), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Bathroom" by Thunder (https://sketchfab.com/3d-models/3eafb89804b54c8e8cbe35e4d456e0a9), CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (licence flag: share_alike)
- "same sink but less sanitary" by GroundZer0 (https://sketchfab.com/3d-models/493b70a6177d4a1385b6b0ce041a93b0), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Mobilya1" by Emre.Topuz (https://sketchfab.com/3d-models/5248aa117842442980a2a2bbb5f3bfe6), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Combo CEG40-50B" by Stala (https://sketchfab.com/3d-models/6458ac945c14458a8e5f4a470495f042), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Ingstav147 PULT ZRK V1" by KRONZI (https://sketchfab.com/3d-models/8580c4545d1649efb3503c6c2a012641), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Sink" by Shining Salt (https://sketchfab.com/3d-models/ce1a06f7cbe1425099a145f851fc5dee), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Bathroom1" by neutralize (https://sketchfab.com/3d-models/f76c502218884914a27148f656a9b656), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Generated industrial toilet (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated japandi toilet (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated japandi toilet (3)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated mediterranean toilet (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated minimal toilet (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated rustic toilet (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated scandinavian toilet (4)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Toilettes" by Lightningx (https://sketchfab.com/3d-models/0b3325fad3e740b1ac86173c90b56afd), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Zenit Close Coupled Push Button Flush Toilet" by Yaiyeondurising (https://sketchfab.com/3d-models/1bd73c9a74d14ce29e45c277570990e6), CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (licence flag: share_alike)
- "Toilet" by Xill (https://sketchfab.com/3d-models/24d1b493899d407780140688abae19bc), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Toilet" by Ali107_YT (https://sketchfab.com/3d-models/3446229dce1f47528fa871cc7669136c), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Memoirs Stately Close Coupled Toilet" by Yaiyeondurising (https://sketchfab.com/3d-models/4398bcb5976945b08f195816340247b8), CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (licence flag: share_alike)
- "Qualitas Bathrooms toilet low poly" by Yaiyeondurising (https://sketchfab.com/3d-models/5b18711616054a44b025d9272b745a6a), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "CWLCCST1-6DT01 Ld" by trendforward (https://sketchfab.com/3d-models/bd0f8d2bfba24376bec2b827a0cbbabe), CC BY-NC 4.0 (https://creativecommons.org/licenses/by-nc/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (licence flag: non_commercial)
- "Animated low poly toilet" by Gamedirection (https://sketchfab.com/3d-models/c901dfa120a0487a9f5c9a2d241f70ab), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Generated industrial shower (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated japandi shower (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated mediterranean shower (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated minimal shower (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated rustic shower (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated scandinavian shower (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated industrial bathtub (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated japandi bathtub (3)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated mediterranean bathtub (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated minimal bathtub (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated modern bathtub (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated modern bathtub (3)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated modern minimal bathtub (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated modern minimal bathtub (2)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated modern minimal bathtub (3)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated scandinavian bathtub (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated scandinavian bathtub (2)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated scandinavian bathtub (4)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "CARBAWH1-6DT01" by trendforward (https://sketchfab.com/3d-models/84d5cdc68a674e12958f41500e988502), CC BY-NC 4.0 (https://creativecommons.org/licenses/by-nc/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (licence flag: non_commercial)
- "Home Corona 2 unità da 1 TV a schermo Piatto, supporto/ripostigli" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian Corona TV Cabinet, Flat Screen Stand Unit, Solid Pine Wood" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet King Street Industrial TV Media Console Table with Three Drawers, Black Metal and Wood, Glass" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet King Street Industrial Cabinet Media Console Table With Functional Storage, Walnut, Black Metal, Glass" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet King Street Industrial Four-Drawer Media Console Table, Walnut, Black Metal, Glass" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Eastport Modern Industrial Entertainment Center Console TV Stand Table, 59"W, Oak" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Ferndale Rustic Reclaimed Pine Media TV Console Stand, 71"W, Sandstone" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Alan Casual Wood Media TV Console Table, 62"W, Washed Navy and Gold" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Traditional Oak Wood Media TV Console Table, 59", Walnut Finish" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Bruckner Casual Wood Media Table, 64"W, Brown" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Bowlyn Mid-Century Modern Wood TV Media Table Stand, 64", Walnut" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Bowlyn Mid-Century Modern Wood TV Media Table Stand, 54", Walnut" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "ROCKPOINT TV Stand, 42x16x23.6inch, Walnut Brown" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Roxmere Mid-Century Modern TV Media Console Center Stand, 59"W, Acacia Wood &amp; Dark Metal" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian TV Unit with Storage, 40 x 154cm, Oak/Timber/High Gloss White" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Movian TV Board for TVs up to 80 Inches" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Corban Contemporary 2-Drawer Media Console, 75"W, Gray" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Corban Contemporary Media Cabinet, 59"W, Gray" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian 2-Door TV Stand, 150 x 41 x 44 cm, White" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian 2-Door 1-Shelf TV Stand, 176 x 40 x 58 cm, White and Oak Effect" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Glenwood Bookcase, 72"H, Oak" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Larson Industrial Wood and Metal 4-Shelf Bookcase, 73"H, Walnut" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Casual Wood Bookcase, 34"W, Natural Rattan" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian Moselle 2-Door Cabinet/Bookcase with 8 Shelves, 139 x 100 x 45cm, Light Brown Oak-Effect/White" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian Oker 2-Door Cabinet/Bookcase with 8 Shelves, 100 x 140cm, Light Brown Oak-Effect/White" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Roxmere Modern Ladder Bookcase, 23.6"W, Acacia Wood and Dark Metal" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Stone & Beam Rylee Modern Bookcase 39.4"Wx76.8”H, Mixed Gray" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Alkove Velle Bookcase, 42 x 95 x 202cm, Oiled Honey Oak" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "AmazonBasics Modern 5-Tier Ladder Bookshelf Organizer with Solid Rubber Wood Frame, Espresso" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "AmazonBasics Classic 5-Shelf Open Bookcase Organizer with Solid Rubber Wood Frame - Espresso" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "AmazonBasics Classic 5-Tier Open Bookcase with Solid Rubber Wood - Walnut" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Davenport Contemporary Shelf, 34"W, Elm and Metal" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam 5-Shelf Bookcase, 75"H, Weathered Oak Finish" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Bookcase" by Bec (https://sketchfab.com/3d-models/4939d1bca386405f9cc22c48441b63de), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Scaffale B" by Francesco Coldesina (https://sketchfab.com/3d-models/68baafb344b2445a8e7f4917b6fe8a63), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Dusty Old Bookshelf (FREE)" by Brandon Westlake (https://sketchfab.com/3d-models/6c5ac2547db34c3c81b2e4808b000386), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Bookcase" by joseph.casey97 (https://sketchfab.com/3d-models/7a545709aa98429a9b30f812f70193f7), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Bookcase" by Icanreed (https://sketchfab.com/3d-models/b43c45317fd74a4aa9ba443b9a355ea3), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "High Bookcase" by 8549 (https://sketchfab.com/3d-models/d48a42e91c5d4716a8c254addf8c9d99), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Solo 100シェルフ WN" by classe-saga (https://sketchfab.com/3d-models/eb98251fbccf4cdd8a3737362e2378e9), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Hallowood Waverly 1 Drawer Small Side Table in Light Oak Finish | Solid Wooden End/Lamp Stand/Bedside Cabinet/Nightstand, (WAV-LAM590)" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Mid-Century Modern Lacquer Side End Table Nightstand, Grey and Walnut" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Cabernet Slatted 3-Drawer Side End Table Nightstand, 18.9"W, Ash" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Newport Nightstand End Table, 22"W, Toffee Oak" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian High Gloss 2 Drawer Bedside Cabinet, Black and Walnut, 47 x 40 x 36 cm" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian High Gloss 2 Drawer Bedside Cabinet, White and Walnut, 47 x 40 x 36 cm" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian High Gloss 3 Drawer Bedside Cabinet, Black and Walnut, 56 x 40 x 36 cm" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian High Gloss 3 Drawer Bedside Cabinet, Black, 56 x 40 x 36 cm" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Ravenna Home Priscilla Modern X-Frame End Table Nightstand, 18.9"W" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Alkove Hayes 1-Drawer Solid Wood Nightstand, 56 x 44 x 47cm, Wild Oak" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Solimo Aquilla Engineered Wood Bedside Table with Drawer (Wenge Finish)" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "AmazonBasics Classic Wood Nightstand End Table with Cabinet - Black Oak" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Claremont Contemporary Nightstand with Tapered Legs, 20"W, Pale Wood and White" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand Movian Emme, Bedside Table, 40 x 40 x 45 cm (L x W x H), High Gloss White" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "AmazonBasics 2-Drawer Bedside Table, 45 x 38 x 49 cm, Light Brown/Dark Grey" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "AmazonBasics - 1-Drawer 1-Shelf Bedside Table, 45 x 38 x 53 cm, Beige with Grey Drawer" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian Kyyvesi, 2-Drawer Storage Night Stand, 60 x 42 x 50 cm, Walnut Effect" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Rivet Mango Wood and Iron 3-Drawer Shutter Nightstand, 18"W, Natural Finish" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Vida Designs Corona Merchant Chest Of Drawers, 9 Drawer, Solid Pine Wood" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian Corona Sideboard, 1 Door 4 Drawer, Solid Pine Wood, 76 x 86 x 40 cm" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Marchio Amazon - Movian, credenze modello Minho, 98 x 90 x 38 cm, quercia Sanremo" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Vida Designs Corona Chest Of Drawers, 4 Drawer, Rustic, Solid Pine Wood." by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Glenwood Industrial Metal Dresser, 60"W, Oak" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Glenwood Industrial Metal Chest of Drawers, 52"H, Oak" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet West, Mid-Century, Oak Distinct Grain, 6-Drawer Dresser, 60"W, Dark Oak Finish" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Parson 6-Drawer Wood Bedroom Dresser, 60"W, Natural" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet West, Mid-Century, Oak Distinct Grain Chest Bedroom Dresser, 38"W, Dark Oak Finish" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Eastport Industrial Wood Dresser, 30"W, Oak Finish" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian Hulio High Gloss 4 Drawer Chest Of Drawers, Black and Walnut, 72 x 75 x 36 cm" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Gould Contemporary Wood Bedroom Dresser Chest, 18", Washed Navy and Gold" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Artum Hill BE6-802 Laurel Dresser, 5-Drawer, Modern Gray" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Artum Hill BE5-539 Kensington Dresser, 6-Drawer, Limestone Gray" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Modern Chest of Drawers with Diamond Pattern 17.3"W, Walnut &amp; Gray Wash" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Modern Chest of Drawers with Diamond Pattern, 17.7 Inch Width, Natural" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Ameriwood Home Classic 6 Drawer Dresser, Espresso" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Ameriwood Home Classic 5 Drawer Dresser, Espresso" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Generated classic washing machine (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated industrial washing machine (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated japandi washing machine (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated japandi washing machine (2)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated japandi washing machine (3)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated mediterranean washing machine (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated minimal washing machine (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated modern washing machine (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated modern washing machine (2)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated modern washing machine (3)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated modern minimal washing machine (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated modern minimal washing machine (2)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated modern minimal washing machine (3)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated rustic washing machine (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated scandinavian washing machine (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated scandinavian washing machine (2)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated scandinavian washing machine (3)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated scandinavian washing machine (4)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Ameriwood Home Carver End Table, Gray/Sonoma Oak" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Mid-Century Modern Round Black Wood Nesting Side End Table, 15.7" W, Dark Oak" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Larson Industrial Wood & Metal Side End Table, 27"W, Walnut" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Ferndale Rustic Reclaimed Pine Side End Table, 24"W, Sandstone" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Modern Rustic Reclaimed Elm Round Accent Side End Table, 16.9"W, Natural" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Stone & Beam Larson Industrial Wood & Metal Side End Table, 22"W, Set of 2, Walnut" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Modern Round Metal Side End Accent Table, 15"W, Black" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Mid-Century Modern Honeycomb Square End/Side/Nesting Tables, Wood and Bronze" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Modern White Marble and Wood Double Storage Wood Shelf Side End Table, 21.3"H, White/Brass/Walnut" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Modern Square Nesting End/Side Tables, Black Metal and Tempered Mirror Glass" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Ravenna Home Aubree Mid-Century Modern Shelf Storage Side Table, 23.6"W, Grey pine" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "2L Lifestyle Harbor Modern Wedge Side End Table,Brown" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Ravenna Home Anne Marie Wood Curved Leg Shelf Storage Side End Table, 20"W, Black" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Ball & Cast End Table" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam 2-Tier Rustic Accent End Table, 26"W, Light Wood and Dark Metal" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Ravenna Home Damask-Pattern Ceramic Garden Stool or Side Table, 16"H, Grey" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Ravenna Home Clover-Pattern Ceramic Garden Stool or Side Table, 16"H, Grey" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Ravenna Home Moroccan-Pattern Ceramic Garden Stool or Side Table, 16"H, Grey" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Industrial Mango-Topped Side Table, 19.61"W" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Rivet Round End/Side Table with 2 Shelves, 40 x 40 x 61 cm, Pine Wood with Walnut-Colour Lacquer/Metal" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Caden Adjustable Task Floor Lamp with Bulb, 60"H, Black and Brass" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Glass Column Brass Floor Lamp, With Bulb, Linen Shade, 13.0" x 13.0" x 59.0", Brushed Brass" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Rivet Mid-Century Modern Theory 5-Arm Living Room Floor Lamp with Edison Light Bulbs, 60"H, Black and Brass Finish" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Rivet Adjustable Tree-Style 3-Light Floor Lamp, 69"H, with Bulbs, Bronze and Brass" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Rivet Olive 4 Wood Shelf Standing Floor Lamp With Light Bulb and USB Charging Station - 11.8 x 11.8 x 62 Inches, Brass" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Mid-Century Modern Floor Lamp with Wireless USB Port Charging Wood Table, 59"H, Light Bulb Included, Black" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Ravenna Home Traditional Standing Floor Lamp with Reading Light and LED Light Bulb - 69.75 Inches, Brushed Nickel with Frosted Glass" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Ravenna Home Frosted Glass Living Room Standing Floor Lamp with LED Light Bulb - 69.75 Inches, Brushed Nickel" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Rustic Storage Space/Shelving Unit Pull Chain Switch Floor Lamp with Bulb, 62"H, Black" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Mid-Century Modern Henley Living Room Standing Floor Lamp with LED Light Bulb - 15 x 15 x 58 Inches, Matte Black and Antique Brass" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Ravenna Home Floor Lamp with Shelves, LED Light Bulb included, 62.75"H, Black" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Ravenna Home Traditional Metal Floor Lamp with Stacked Oval Accents, LED Bulb Included, 58.5"H, Polished Nickel" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Generated japandi floor lamp (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated japandi floor lamp (2)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Street Lamp" by emelyarules (https://sketchfab.com/3d-models/01c53767c1f84f55ad9f46eb89949cf9), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Lamppost" by martn00 (https://sketchfab.com/3d-models/0a34dc814a3a44cfa76388e732c05376), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "lamp" by anish_ (https://sketchfab.com/3d-models/0eba4ad785674d3586aafc82854100fa), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Floor Lamp" by bilgehan.korkmaz (https://sketchfab.com/3d-models/33eb258d9873435690254cfbb0ea46ec), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "low poly Lamp 3d model" by mohamedvfx (https://sketchfab.com/3d-models/53409613b45b42b98b979f12ab8faa12), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Street lights" by U-like (https://sketchfab.com/3d-models/71853da424aa4b208e14f6cf430339ae), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Generated industrial potted plant (2)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated japandi potted plant (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated japandi potted plant (2)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated japandi potted plant (3)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated mediterranean potted plant (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated minimal potted plant (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated modern potted plant (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated modern minimal potted plant (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated rustic potted plant (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated scandinavian potted plant (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated scandinavian potted plant (2)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated scandinavian potted plant (3)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Empty Flower Pot" by dumerlot (https://sketchfab.com/3d-models/41e58efcf647494483f9860df99acf60), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "succulent" by Elif Smbl (https://sketchfab.com/3d-models/57972124483145b4a4bbf4fd4caca6e7), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Cacti pot" by Spacyy (https://sketchfab.com/3d-models/71b53eaee72e4a829a9256a7bcfb7dab), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Succulent" by mika.rr (https://sketchfab.com/3d-models/9dd44cda400c48a083ffd9480067f04f), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "FlowerPot" by ibrahmcingi (https://sketchfab.com/3d-models/b99c584dd11d4691b5d13303383371e5), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "CGT 116 Wk8 Plant" by mlin234 (https://sketchfab.com/3d-models/bf122cd0854e422bb94704552c64810b), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Velvet Texture Decorative Throw Pillow, 17" x 17", Midnight" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Striated Velvet Linen-Look Decorative Throw Pillow, 17" x 17", Midnight" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Modern Geometric Decorative Print Throw Pillow, 20" x 20", Teal" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Mojave-Inspired Decorative Throw Pillow Cover, 20" x 20", Black and Red" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Transitional Woven Diamond Decorative Throw Pillow, 20" x 20", Indigo" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Transitional Woven Diamond Decorative Throw Pillow Cover, 20" x 20", Indigo" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Modern Geometric Decorative Print Pillow Cover, 20" x 20", Black" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Modern Geometric Decorative Print Pillow Cover, 20" x 20", Teal" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Yard-Dyed Shibori Decorative Throw Pillow Cover, 17" x 17", Blue" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Abstract Geometric Throw Pillow Cover, 20" x 20", Ivory" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Modern Abstract Geometric Decorative Throw Pillow, 20" x 20", Cover Only, Purple" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Abstract Geometric Throw Pillow, 20" x 20", Ivory" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Modern Abstract Geometric Decorative Throw Pillow, 20" x 20", Purple" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Modern Retro Flair Mosaic Geometric Decorative Throw Pillow, 20" x 20", Cover Only, Blue" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Modern Abstract Circle Throw Pillow Cover - 20 x 20 Inch, Grey" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Modern Mosaic Throw Pillow - 20 x 20 Inch, Blue" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Abstract Pattern Throw Pillow Cover - 20 x 20 Inch, Grey" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Casual Pom-Pom Throw Pillow - 24 x 12 Inch, Mineral" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Modern Macrame Fringe Lumbar Throw Pillow - 18 x 12 Inch, White" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Ravenna Home Casual Floral Throw Pillow, 20" x 20", Cream and Blue" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Shaggy Short Rug, 7'7" x 9'7", Ivory" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Mid-Century Modern Dusk Wool Rug, 5' x 8', Tan" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Rivet Woven Bordered Sisal Area Rug, 3' 6'' x 5' 6'', Natural" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Diamond Trellis Tassel Wool Rug, 7'6" x 9'6", Ivory" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Stone & Beam MFL nuLoom Rug B0719STLSH 5'X8' Cream" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Modern Wave Cosmopolitan Area Rug, 8 x 10 Foot, Beige" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "nuLOOM Leaflet Fountain Boho Wool Area Rug, 7' 6" x 9' 6", Pink" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Swirling Paisley Farmhouse Motif Wool Runner Rug, 2' 6" x 8', Multi" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Contemporary Striated Jute Area Rug, 10' 6" x 8', Oatmeal" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Contemporary Striated Jute Rug, 7' 5" x 5' 3", Brick" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Contemporary Diamond Patterned Area Rug, 7'4" x 5'3", Grey Ivory" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Geometric Wool Area Rug, 5 x 8 Foot, Blue, Ivory" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Contemporary Striated Jute Rug, 13' x 9' 3", Aegean Blue" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Contemporary Striated Jute Area Rug, 5' 9" x 3' 9", Silver Birch" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Modern Chevron Wool Area Rug, 5' x 8', Blue, Green, Ivory" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Contemporary Striated Jute Area Rug, 10' 6" x 8', Off White" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Contemporary Striated Jute Rug, 10' 6" x 8', Citron" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Stone & Beam Rug, 3'11" x 5'11", Blue, Navy, Multicolor" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Stone & Beam Polypropylene Round Rug, 5'3" x 5'3", Gray, Orange, Multicolor" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Basics - 4'X6' Plush Diamond Trellis Shag Rug, Grey" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Modern Print Wall Art of Brooklyn Bridge Sketch, Black Frame, 18" x 26"" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Modern Red and Gold Tulip Print on Canvas, Brown Frame, 13.75" x 13.75"" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Aerial View Black, White and Gold Floral Canvas Print Wall Art, 16" x 16"" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Patterned Color Circles Wall Art in White Frame, 26" x 38"" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Modern Gold Print of 1885 Baseball Bat Patent, Black Frame, 15" x 21"" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet World Map Hemisphere Print in Black and White Vintage Wall Art, Black Frame, 30.5" x 30.5"" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Patterned Modern Pink and Grey Triangles in White Frame Wall Art, 18" x 26"" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Modern Metallic Ink Reprint of Sailing Ship Patent Wall Art, Silver Frame, 15" x 21"" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Black and White Vintage Bike Print in White Frame, 15" x 21"" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Modern Black and White Desert Cactus Photo on Wood, White Frame, 20" x 20"" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Modern Gold Pyramid Triangle Print Wall Art, 30" x 30", Black Frame" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Abstract Topographic Print in Black Wood Frame, 20" x 20"" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Modern White Framed Black and White Paris Map Print, 30" x 30"" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Modern Turquoise and Orange Palm Print in Gray Frame Wall Art, 12" x 12"" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Vintage Blue Yellow and Green Chairs in Gold Wood Frame Wall Art, 20" x 20"" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Abstract Asian Influenced Grey and Black Print on Canvas Wall Art Decor, 36"W x 24"H" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Traditional Landscape Print with Copper Leaf Wall Art Decor on Canvas - 35" x 35"" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Modern Decorative Ceramic Vase Decor With Geometric Pattern, 7.7 Inch Height, White" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Rustic Stoneware Indoor Outdoor Flower Plant Home Decor Tall Cylinder Vase, 11"H, Silver" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Rustic Stoneware Indoor Outdoor Flower Plant Home Decor Tall Cylinder Vase, 11"H, Bronze" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Rustic Stoneware Indoor Outdoor Flower Plant Home Decor Cylinder Vase, 9"H, Silver" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Rustic Stoneware Indoor Outdoor Flower Plant Home Decor Cylinder Vase, 9"H, Bronze" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Modern Round Ceramic Home Decor Flower Vase - 7 Inch, Coral White Tan" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Modern Ceramic Home Decor Flower Vase - 7 Inch, Teal White Tan" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Mid Century Modern Round Ceramic Home Decor Flower Vase - 5 Inch, Blue and Green" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Modern Ceramic Home Decor Flower Vase - 11.75 Inch, Coral White Tan" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Modern Ceramic Home Decor Flower Vase - 7 Inch, Teal White Tan" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Westline Modern Indoor Outdoor Hand-Painted Stoneware Flower Vase, 9.5"H, Red White Blue Black" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Westline Modern Indoor Outdoor Hand-Painted Stoneware Flower Vase, 9.5"H, Yellow White Blue Black" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Textured Modern Vase, 15.86"H, Blue" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Textured Modern Vase, 12.4"H, White" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Mid-Century Feather Vase, 8.66"H, Neutral and Gold" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Ravenna Home Mid-Century Stoneware Vases, Set of 3, 4.8"H, 3 colors" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Modern Stoneware Vase, 10.51"H, Blue and Sand" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Mid-Century Rustic Vase, 8.66"H, Neutral" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Textured Modern Vase, 9.05"H, Gray" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Mid-Century Metallic Stoneware Vase, 11.8"H, Gold" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Generated industrial bowl (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated japandi bowl (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated mediterranean bowl (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated minimal bowl (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated modern bowl (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated modern minimal bowl (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated rustic bowl (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated scandinavian bowl (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated scandinavian bowl (2)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated classic plant small (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated industrial plant small (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated japandi plant small (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated mediterranean plant small (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated minimal plant small (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated modern plant small (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated modern minimal plant small (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated rustic plant small (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated scandinavian plant small (1)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Generated scandinavian plant small (2)": generated with TRELLIS.2-4B (MIT) for WenArt_RUN; no third-party credit
- "Amazon Brand – Stone & Beam Modern Bedroom Table Desk Lamp With Light Bulb - 8 x 8 x 20.5 Inches, Wood Grain" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Glass Column Living Room Table Desk Lamp With Light Bulb and Linen Shade, 23"H, Black" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Copper Geometric Bedside Table Desk Lamp With Light Bulb - 16.75 Inches, Copper" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Rivet Pike Factory Industrial Table Lamp With Light Bulb - 6 x 13 x 19 Inches, Brushed Steel" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Rivet Mid Century Modern Rubberwood Living Room Table Lamp With Light Bulb - 19 Inches, Black with Linen White Shade" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Rivet Wood and Black Marble Lamp, Mid-Century Walnut, With Bulb, 18"H" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Rivet Modern Deer Head Ceramic Lamp With Bulb, 19.5"H, White and Brass" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Mid-Century Modern Curved Task Desk Table Lamp With USB Port And Light Bulb - 26 Inches, Matte Black &amp; Brushed Steel" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Ravenna Home Accent Table Lamp with LED Light Bulb -18.5 Inches, Brushed Nickel with White Shade" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Modern Farmhouse Wood Cylinder Table Desk Lamp With LED Light Bulb And White Shade- 14 x 14 x 27 Inches" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Rivet Contemporary Palm Tree Neon Table Lamp, 11.75"H, White AF44228" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Mid-Century Modern Cone Nightstand Table Desk Lamp with LED Light Bulb - 15 Inches, Black and Gold" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Modern Two Tone Table Desk Lamp with LED Light Bulb and Drum Shade - 12 x 12 x 15.88 Inches, Matte Black and Antique Brass" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Ravenna Home Metal Table Lamp with LED Light Bulb, 20"H, Dark Bronze" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Ravenna Home Classic Straight Banker's Task Desk Lamp with LED Light Bulb, 16"H, Brushed Nickel" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Ravenna Home Round Base Table Lamp with LED Light Bulb, 20"H, Dark Bronze" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Two-Toned Ceramic Base Table Lamp, Bulb Included, 19.75"H, Beige" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Ravenna Home Traditional Metal Downbridge Desk Lamp with Adjustable Shade, LED Bulb Included, 19.25"H, Brushed Nickel" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Scandinavian Real Blond-Wood Table Lamp with Marble Bottom, LED Bulb Included, 18.5"H, Beige" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Scandinavian Real Wood Table Lamp with Faux Marble Base, LED Bulb Included, 17.5"H, Gray Wood" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Iron Latticework Decorative Hanging Mirror Wall Art, 39.4 Inch Height, Verdi Green" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Rustic Wood and Rope Geo Mirror, 36" H, Natural" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Round Wood Quadrant Hanging Wall Mirror, 15 Inch Height, Dark Wood Finish" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Square Wood Quadrant Hanging Wall Mirror, 15 Inch Height, Dark Wood Finish" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Sunburst Lines Hanging Wall Mirror Decor, 20 Inch Height, Antique Gold Finish" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Jonathan Mid-Century Modern Mirror Wood Frame, 52", Walnut" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Rustic Farmhouse Round Wood Iron Mirror with Faux Leather Strap - 22 Inch, Black Metal" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Basics Rectangular Wall Mirror 16" x 20" - Peaked Trim, White" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Basics Rectangular Wall Mirror 30" x 40" - Peaked Trim, White" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Basics Rectangular Wall Mirror 30" x 40" - Standard Trim, Walnut" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Basics Rectangular Wall Mirror 24" x 36" - Standard Trim, Black" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Ravenna Home Vintage Wooden Accent Mirror, 27.75"H, Natural" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Rivet Modern Rhombus Cutout Hanging Mirror, 26.75"H, Gold" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Rivet Modern Round Hanging Mirror with Shelf, 18" Diameter, Gold" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Rivet Modern Round Cutout Hanging Mirror, 22.25" Diameter, Gold" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Rivet Modern Oval Hanging Mirror, 39"H, Gold" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Rivet Modern Cutout Hanging Mirror, 23"H, Gold" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched

## Refused after judging

| uid | Source | Type | Reason |
|---|---|---|---|
| 00b360de1846428eb5c23464824c5fc8 | objaverse | toilet | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry +X |
| 0102b2c1449f448687d62ea66ae2a26a | objaverse | chair | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 33 of 38 accepted chair models (keep 20) |
| 01b79647e6e442989fda47ff20cabdc9 | objaverse | armchair | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 34 of 36 accepted armchair models (keep 20; its styles classic had 5 each in the first pass) |
| 01dac0f367544b28a32ef3e276e3106e | objaverse | washbasin | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| 03cba69a2c3140f7abc013d42d455fba | objaverse | sofa | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 35 of 38 accepted sofa models (keep 20; its styles modern minimal, minimal, modern had 5 each in the first pass) |
| 03f16302c1a54c46b438dac78e9d7048 | objaverse | chair | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 31 of 38 accepted chair models (keep 20; its styles modern minimal, modern had 5 each in the first pass) |
| 03febdfb56cf419d89fe2d4eaa0bdb5e | objaverse | table_coffee | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 04bef8e589524b8c9d7a3bb206b206a8 | objaverse | potted_plant | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 05a4c8fccea2443f8bc67e4b3152e056 | objaverse | wardrobe | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry +Y |
| 072d0468bb97447ab1ca7e3edea25f1f | objaverse | sofa | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 29 of 38 accepted sofa models (keep 20; its styles classic had 5 each in the first pass) |
| 08d73e1168504bf2b8706cd838ad16ef | objaverse | bookshelf | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 23 of 24 accepted bookshelf models (keep 20; its styles modern had 5 each in the first pass) |
| 0972c48a7e4548bca80975a47a823bab | objaverse | bed_double | front not agreed (judges and geometry or the documented front): judges: view 3 (-X); geometry +Y |
| 09ee59423b4b428f94f01fc5beccd227 | objaverse | armchair | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 21 of 36 accepted armchair models (keep 20; its styles classic had 5 each in the first pass) |
| 0cb0a6704c8a4fbd967039998a9d76ac | objaverse | bed_double | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 22 of 22 accepted bed_double models (keep 20; its styles scandinavian, modern had 5 each in the first pass) |
| 12f297af37e9444dae34a02e86c4d36b | objaverse | potted_plant | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 132a8ee2af3a40d39d270fbed3d3666c | objaverse | toilet | front not agreed (judges and geometry or the documented front): judges: qwen 1, glm 0 |
| 13407a0758804fc09ec4c7e51e9f9d0e | objaverse | chair | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 35 of 38 accepted chair models (keep 20) |
| 138f793adde045a5a5247edf48f61eb1 | objaverse | sofa | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 20 of 38 accepted sofa models (keep 20; its styles modern minimal, modern had 5 each in the first pass) |
| 14791efb33314b02ac5ac74b47c36d14 | objaverse | bookshelf | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry undecided (open_side: panel fractions {'-x': 1.0245, '+x': 1.0313, '-y': 0.1149, '+y': 0.2505} give 0 axes with one closed side) |
| 15a583ac9db84a529e7ea1d2bd7eadbe | objaverse | fridge | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| 17c796aeb1b8455d8f594a72490e11b7 | objaverse | washbasin | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 1a41218e823c4cba801bd2b3d71c9dff | objaverse | wardrobe | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 1b48a3d913474e6890b8b8163bb5407c | objaverse | fridge | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| 1bf49e047db04dabab8a1665e88af5e6 | objaverse | toilet | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| 1c74372d1aeb4bf2abb90358352d4282 | objaverse | washbasin | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| 1d18955742df45e9875b28d382a33ef3 | objaverse | wardrobe | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry +Y |
| 1d2f3157246e4eb3818a50a6732ca05e | objaverse | stove | not a single object (a judge): qwen False, glm True |
| 1d41e84fd76241e7a8929a314052269c | objaverse | table_coffee | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 28 of 33 accepted table_coffee models (keep 20; its styles scandinavian, japandi, modern minimal, minimal, modern had 5 each in the first pass) |
| 1f07c148a7bc4e7c88dc57de50dc36b3 | objaverse | toilet | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry undecided (back_taller: offsets -0.057 (x) and +0.092 (y) do not single out one axis) |
| 1fdb702ad88e41e2b90a5af4037bbfd3 | objaverse | washbasin | front not agreed (judges and geometry or the documented front): judges: qwen 2, glm 0 |
| 23fa151346304c8bb8c58f58a76e6407 | objaverse | desk | front not agreed (judges and geometry or the documented front): judges: qwen 1, glm 3 |
| 240796c1b98b424381195e8b4c7f83e9 | objaverse | washbasin | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 2556bb64f1414de7afb8a299097ef279 | objaverse | fridge | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| 257f44c12fa948deacca9995dbb70e7b | objaverse | potted_plant | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| 26b5f6c3ceb640d78829c0293c3ffbf9 | objaverse | table_dining | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 2a725ae04a33493fad2ee6dad98a85af | objaverse | washbasin | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| 2b14055dc8054ec79b4d0d7e8f00be1e | objaverse | floor_lamp | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 25 of 33 accepted floor_lamp models (keep 20; its styles modern had 5 each in the first pass) |
| 2b7d5c96159c42589dd970d81e877668 | objaverse | toilet | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 2bd3fcc82c9f43cfb0c8cf26c7d0107c | objaverse | bed_double | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 20 of 22 accepted bed_double models (keep 20; its styles modern minimal, modern had 5 each in the first pass) |
| 2c32127e0a354be9b588bbeb8f9ac644 | objaverse | chair | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 36 of 38 accepted chair models (keep 20) |
| 2dc08ab4103e43e3968ae45e59231c06 | objaverse | toilet | not a single object (a judge): qwen False, glm True |
| 2e0afa27358f4223b658e8351002d19f | objaverse | fridge | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| 2e762d68e7ae4ac1a49553c03c940c61 | objaverse | bathtub | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| 2f1706233a3248cf9a74586fc2e7120c | objaverse | bathtub | front not agreed (judges and geometry or the documented front): judges: qwen 2, glm 0 |
| 2fdaa56bbd85404cb4206dcaedc16658 | objaverse | fridge | front not agreed (judges and geometry or the documented front): judges: view 1 (+X); geometry -X |
| 2ffb917efef043dbb7fe98f44d2d9b2b | objaverse | stove | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| 300ece91863242649e728e2f8d2a6bfe | objaverse | desk | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 26 of 26 accepted desk models (keep 20; its styles modern minimal, minimal, modern had 5 each in the first pass) |
| 305f2b09e0de48bb919116026aba8f44 | objaverse | potted_plant | not the furniture type (a judge): qwen False, glm True |
| 309ccba7b2cb40a6bfffb89f498fc54c | objaverse | wardrobe | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry undecided (detail_side: vertex counts {'-x': 96, '+x': 96, '-y': 50, '+y': 51} give no side with 1.3x more detail) |
| 30b975722e7e4d8694ee9628cd669177 | objaverse | toilet | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 317dac94ec404bdbaa6d41a85e04f51c | objaverse | floor_lamp | not the furniture type (a judge): qwen False, glm True |
| 319ec67c98e447eebda0039b143274c5 | objaverse | bookshelf | front not agreed (judges and geometry or the documented front): judges: qwen 1, glm 3 |
| 322ba3a159a845c7b7642467e23fcc2d | objaverse | bed_single | front not agreed (judges and geometry or the documented front): judges: qwen 1, glm 3 |
| 3301331424bb4dbc8f06e2d3717bb067 | objaverse | floor_lamp | not the furniture type (a judge): qwen False, glm False |
| 34b12514108a4ffd897c9324a4a35858 | objaverse | washbasin | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 351d798f9cc3451099200c5235aee352 | objaverse | chair | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 37 of 38 accepted chair models (keep 20) |
| 3597a7a470ac4f81b1b362eea66f4d6f | objaverse | wardrobe | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 36f12a0c9c9149aab3dbe7fb35189fee | objaverse | table_coffee | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 20 of 33 accepted table_coffee models (keep 20; its styles modern minimal, minimal, modern had 5 each in the first pass) |
| 385c09d2ebb2483d96a78918c665db51 | objaverse | bathtub | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| 39541d5daa7a4fba9614ad9847c992d5 | objaverse | desk | front not agreed (judges and geometry or the documented front): judges: qwen 2, glm 0 |
| 3b1033c7d6c84db8b0850121363b65ef | objaverse | potted_plant | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| 3d118a9fd6e34ddab99cb0fab5540682 | objaverse | bed_single | front not agreed (judges and geometry or the documented front): judges: qwen 2, glm 0 |
| 3de2e575e8b941dd94ae08158636b20a | objaverse | table_dining | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 3ee00f7e14674461af4241f5ef7ed039 | objaverse | desk | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| 4112e07e262842c6b7070aa1505505c3 | objaverse | wardrobe | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry +Y |
| 426c14adba6a45638752986c2f7d16b2 | objaverse | bed_double | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 42da0122f2134a189767d0911b401c1c | objaverse | sofa | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 32 of 38 accepted sofa models (keep 20; its styles modern minimal, modern had 5 each in the first pass) |
| 46e8f848735b496e8aeda829d0b96023 | objaverse | fridge | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 4825d2d251b648f583db7147a7fd8d63 | objaverse | potted_plant | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 482c5168f1694911b597c81f3d0c73b1 | objaverse | sofa | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 36 of 38 accepted sofa models (keep 20; its styles modern minimal, modern had 5 each in the first pass) |
| 4a0f306ba95144fda533b329818d0680 | objaverse | floor_lamp | not the furniture type (a judge): qwen False, glm False |
| 4ae706aa53c043fa8261ebf40f580303 | objaverse | potted_plant | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| 4fdd0158c80c4de2a1b1bd5e0c77543a | objaverse | desk | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 51d928b33e5549898cc86cbdaf966d83 | objaverse | bookshelf | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 22 of 24 accepted bookshelf models (keep 20; its styles modern minimal, minimal had 5 each in the first pass) |
| 531e32a371004849bd72a507aaf81643 | objaverse | toilet | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 536dbfc2fdbe4dec9203ab390b9a6eda | objaverse | bathtub | front not agreed (judges and geometry or the documented front): judges: qwen 2, glm 0 |
| 53ad8efeb5e9427a901fc669b440e3cf | objaverse | fridge | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| 55325e3b09ac48b2ae3803bccf804741 | objaverse | fridge | front not agreed (judges and geometry or the documented front): judges: qwen 1, glm 3 |
| 568f22034e364caca4e450a6d534dbd6 | objaverse | bed_double | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| 57d2004875be4878b25493723cf45469 | objaverse | fridge | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| 580ba3b412a24ee29c62a9ccf6bdc80c | objaverse | stove | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 5847113c458f4a2483aedd663376c7de | objaverse | table_dining | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 22 of 26 accepted table_dining models (keep 20; its styles minimal, modern had 5 each in the first pass) |
| 592d31f4896948bb9ac5e53ac246d8c8 | objaverse | stove | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| 592e740e6310420e957657c16d830102 | objaverse | desk | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 23 of 26 accepted desk models (keep 20; its styles modern had 5 each in the first pass) |
| 5a0ba464174e4dbe94aecfe1a036ca6a | objaverse | fridge | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 5ab48fd4819745b596df3ea39908e2e7 | objaverse | table_coffee | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 33 of 33 accepted table_coffee models (keep 20; its styles modern minimal, minimal had 5 each in the first pass) |
| 5dbfe3c5798445a5bdff4efca0b943a2 | objaverse | bed_single | front not agreed (judges and geometry or the documented front): judges: qwen 1, glm 3 |
| 5e87752d56cd45bebaeac48ba934aaa4 | objaverse | toilet | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 5ec9697d85654005b27fd29bd6df987e | objaverse | sofa | front not agreed (judges and geometry or the documented front): judges: qwen 2, glm 0 |
| 5f235f066a9a416fb7177496a9117ec7 | objaverse | table_dining | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 23 of 26 accepted table_dining models (keep 20; its styles modern minimal, modern had 5 each in the first pass) |
| 604886640ac948f1980d81bc4a3ed7cf | objaverse | bed_double | front not agreed (judges and geometry or the documented front): judges: qwen 1, glm 0 |
| 624c9f7dcb2f4acd93237591ef10c76a | objaverse | chair | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 63797942d2674b6da5c94ce19672e6b6 | objaverse | chair | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 10 of 38 accepted chair models (keep 20; its styles classic had 5 each in the first pass) |
| 653a622f383244ab9e7859f9aa2dcc8f | objaverse | bed_single | front not agreed (judges and geometry or the documented front): judges: view 3 (-X); geometry -Y |
| 65a13a04056c4f51a9c324e2a975b9a5 | objaverse | bed_double | not the furniture type (a judge): qwen False, glm True |
| 65e5c193702e4be9beb5ec783c422b5e | objaverse | chair | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| 674b6c07743e4f569d4b745949d1a0f1 | objaverse | bathtub | front not agreed (judges and geometry or the documented front): judges: qwen 3, glm 2 |
| 67b04f8e125e4ae4adacb3fc42d0016f | objaverse | stove | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| 68ef91781477491e8a25dbe2c7877dbf | objaverse | washbasin | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 68f2b9fd83b349f9b285c360c447edbf | objaverse | table_coffee | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 31 of 33 accepted table_coffee models (keep 20; its styles japandi, modern minimal, modern had 5 each in the first pass) |
| 6c6a1f5757b34f7485133a91bb85cabe | objaverse | bathtub | not a single object (a judge): qwen False, glm True |
| 6ef03a9e81e74b7ab8e98baf512e7e64 | objaverse | toilet | front not agreed (judges and geometry or the documented front): judges: qwen 0, glm 3 |
| 6f79223d321047059e1032c78b1b00a5 | objaverse | table_coffee | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 19 of 33 accepted table_coffee models (keep 20; its styles scandinavian, japandi, modern minimal, minimal, modern had 5 each in the first pass) |
| 6f7bb38a14544f65902b10ec921fe57e | objaverse | armchair | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 23 of 36 accepted armchair models (keep 20; its styles classic had 5 each in the first pass) |
| 70b7b418af714050aa83e99deb2253b7 | objaverse | wardrobe | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry +Y |
| 71af93b1d15f4f48ad836d36110626f7 | objaverse | bookshelf | no style both judges name: qwen ['modern minimal', 'minimal', 'japandi', 'scandinavian'], glm ['modern', 'neutral'] |
| 736e3ea67480426da4013dbca5fb8d20 | objaverse | sofa | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 34 of 38 accepted sofa models (keep 20; its styles modern minimal, minimal, modern had 5 each in the first pass) |
| 73bda35b6e7a499a80427fc1b049b192 | objaverse | washbasin | front not agreed (judges and geometry or the documented front): judges: qwen 1, glm 0 |
| 757961eb75a64dc689f2047ae8cdbd3b | objaverse | wardrobe | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 75aa9519195647d99cf1e2d4863dbe87 | objaverse | bookshelf | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry undecided (open_side: panel fractions {'-x': 0.8648, '+x': 0.8528, '-y': 0.0033, '+y': 0.0} give 0 axes with one closed side) |
| 75f663417e874f24b864348a5c9c3e68 | objaverse | bathtub | front not agreed (judges and geometry or the documented front): judges: qwen None, glm None |
| 774971f63ea54cdba8119439f4ff09c5 | objaverse | table_dining | photoreal quality below 4 (a judge): qwen 3, glm 5 |
| 77c0313ad21144dcb904915d66a163b3 | objaverse | bookshelf | front not agreed (judges and geometry or the documented front): judges: qwen 2, glm 3 |
| 7aa2f0637fde49fca76cd0651936dec4 | objaverse | desk | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| 7ad37a39f5534d57bfb68f34fe0fbd22 | objaverse | potted_plant | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 7b13b36ba2304912afc9840caea731c6 | objaverse | bed_single | front not agreed (judges and geometry or the documented front): judges: view 3 (-X); geometry undecided (back_taller: top centroid offset -0.006 of the extent on x is below 0.08: no taller side) |
| 7d5367e51dca4a50a101b1089149ccde | objaverse | wardrobe | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry +Y |
| 7e7cc43a2fb84e44a03a67fecdd76ba8 | objaverse | desk | front not agreed (judges and geometry or the documented front): judges: view 1 (+X); geometry undecided (detail_side: only 2 vertices at the x sides) |
| 7f92080d86484d81b8dd30317bb28586 | objaverse | desk | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 25 of 26 accepted desk models (keep 20; its styles modern minimal, minimal, modern had 5 each in the first pass) |
| 8002b22408aa4247ba8827cb6df9e52f | objaverse | washbasin | front not agreed (judges and geometry or the documented front): judges: qwen 3, glm 0 |
| 800d3c5569b94abfa2da7976504d589d | objaverse | bathtub | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry +Y |
| 804fa46335874949938b6dfb55d17820 | objaverse | bathtub | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry +Y |
| 8096984ae8734db9bfa5dedf89c175a7 | objaverse | sofa | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 28 of 38 accepted sofa models (keep 20; its styles modern had 5 each in the first pass) |
| 813f5aeef3f3430d947f3879c6941719 | objaverse | floor_lamp | no style both judges name: qwen ['classic'], glm ['neutral'] |
| 815bd9cee3644f3f8996b4a6d123c7c3 | objaverse | desk | front not agreed (judges and geometry or the documented front): judges: qwen 2, glm 0 |
| 8170cf1409924abc9c3fc8becccdd36e | objaverse | floor_lamp | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 28 of 33 accepted floor_lamp models (keep 20; its styles modern had 5 each in the first pass) |
| 81ada0e24e1647d8a0d6d0708a696f84 | objaverse | bed_single | front not agreed (judges and geometry or the documented front): judges: qwen 2, glm 0 |
| 821c4d9f12294380a9b0757b4adbb379 | objaverse | table_coffee | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 21 of 33 accepted table_coffee models (keep 20; its styles japandi, modern minimal, minimal, modern had 5 each in the first pass) |
| 87eab647ca624962a7c178c0105643aa | objaverse | bookshelf | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 24 of 24 accepted bookshelf models (keep 20; its styles modern minimal, minimal, modern had 5 each in the first pass) |
| 887092793d0b402e8571eda2d1a47cb4 | objaverse | potted_plant | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| 8a22e1fd8600472597bfe478e7d0c9ba | objaverse | armchair | front not agreed (judges and geometry or the documented front): judges: view 1 (+X); geometry undecided (back_taller: offsets -0.181 (x) and -0.142 (y) do not single out one axis) |
| 8a983b17bc484fedbc1ead6eb61b55b5 | objaverse | stove | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| 8b099a2dfafc4436890eeaa7e928fd9b | objaverse | floor_lamp | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| 8cd4ef86c0914b95a181473230c77eda | objaverse | stove | front not agreed (judges and geometry or the documented front): judges: qwen 1, glm 0 |
| 8d66a96bf8de4bb1b65c941b2bee65e4 | objaverse | fridge | front not agreed (judges and geometry or the documented front): judges: view 1 (+X); geometry -X |
| 8e1fddb38fa8400c9fcc784abe29aaaa | objaverse | fridge | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry +Y |
| 8ebdabed48ed4963887435aa05f0b874 | objaverse | armchair | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 8fba1e7048c0421fb7e6b6e8be8fce88 | objaverse | stove | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 90a0093f27f04ea19e33591f22910741 | objaverse | wardrobe | no style both judges name: qwen ['classic'], glm ['scandinavian', 'rustic', 'neutral'] |
| 9155b2b4be5f452a98837459112a3b9b | objaverse | potted_plant | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 9234d8196b73434684bcbb8092cc9e2a | objaverse | chair | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 29 of 38 accepted chair models (keep 20; its styles classic had 5 each in the first pass) |
| 93ce115ac08d4365bc9a8d9e386bd166 | objaverse | desk | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry undecided (detail_side: vertex counts {'-x': 326, '+x': 314, '-y': 84, '+y': 84} give no side with 1.3x more detail) |
| 948411a1c6d0453e96faa3dfe32936a0 | objaverse | bathtub | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| 94e8a30e011a49a7a13910139d8daf8f | objaverse | toilet | front not agreed (judges and geometry or the documented front): judges: qwen 0, glm 3 |
| 955cf512b86c4a799aa3ef391d670e55 | objaverse | wardrobe | front not agreed (judges and geometry or the documented front): judges: view 3 (-X); geometry undecided (detail_side: x ratio 1.47 and y ratio 1.43 do not single out one axis) |
| 961af2daa6344e4fba0c7a4c92ff91f8 | objaverse | bookshelf | front not agreed (judges and geometry or the documented front): judges: view 3 (-X); geometry undecided (open_side: panel fractions {'-x': 0.0, '+x': 0.0, '-y': 0.8192, '+y': 0.8192} give 0 axes with one closed side) |
| 978be96600a0434e853c938e93b9c893 | objaverse | armchair | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 98b39c575de547a483f8fbaec2c0242f | objaverse | potted_plant | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| 9a2c5ed79d634a61b1166836a8a5530f | objaverse | sofa | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 9b1e09abe5e34d6397937ebf59901898 | objaverse | sofa | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 30 of 38 accepted sofa models (keep 20; its styles modern minimal, modern had 5 each in the first pass) |
| 9c242421a7c1447f941f72b57e7473e5 | objaverse | sofa | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 31 of 38 accepted sofa models (keep 20; its styles modern minimal, modern had 5 each in the first pass) |
| 9c4935439367490b8039a3cad9c46243 | objaverse | sofa | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| 9f067b405463412883cf2cb5a478079c | objaverse | stove | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| a0d66f10a850469c9cb04c3cecc62a05 | objaverse | sofa | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| a4d6a4618f554e5986fd94e04720488c | objaverse | armchair | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 35 of 36 accepted armchair models (keep 20; its styles classic had 5 each in the first pass) |
| a51e4acfdbb349c7876d7c37d2a0ee87 | objaverse | chair | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 23 of 38 accepted chair models (keep 20; its styles minimal, modern had 5 each in the first pass) |
| a59b3dc728ff45d48a053758a153249b | objaverse | stove | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| a5e397b1cdf3457a99573683198bdcea | objaverse | toilet | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| a5eea808dc20404cb5f9e05680f7362f | objaverse | wardrobe | not the furniture type (a judge): qwen False, glm True |
| a63717d314ea41fd865669f58db82fce | objaverse | washbasin | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry undecided (back_taller: offsets -0.194 (x) and +0.137 (y) do not single out one axis) |
| a755d424dd1d4a69a854ac02f7f86f83 | objaverse | armchair | front not agreed (judges and geometry or the documented front): judges: view 3 (-X); geometry undecided (back_taller: offsets +0.167 (x) and +0.126 (y) do not single out one axis) |
| a82bff9b83be4072871d3e2afc6cec14 | objaverse | fridge | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry +X |
| a8d11ec939064c009b726de5dcedbda2 | objaverse | potted_plant | not the furniture type (a judge): qwen False, glm True |
| a9917037f0c643dbbde0475b59bc53b1 | objaverse | table_coffee | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| aa9a7f23471a4bb6b461d5240c2bf1a7 | objaverse | bookshelf | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry undecided (open_side: panel fractions {'-x': 0.2845, '+x': 0.2274, '-y': 0.0427, '+y': 0.1454} give 0 axes with one closed side) |
| ab89c948efab4b9eaf12d9f0e72acab7 | objaverse | toilet | not a single object (a judge): qwen False, glm True |
| abbf0e6901484c05a68d2c6c485bdd9e | objaverse | table_coffee | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B00NUS53CY | abo | bookshelf | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B00NUS5GXA | abo | bookshelf | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B00TOAN83I | abo | mirror | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B015IPNVFW | abo | wardrobe | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B01LYBQXRH | abo | bookshelf | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| abo_B01M4OYBOI | abo | table_coffee | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 24 of 33 accepted table_coffee models (keep 20; its styles scandinavian, japandi, modern minimal, minimal, modern had 5 each in the first pass) |
| abo_B01M642Q91 | abo | table_coffee | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B01NCOR0VZ | abo | table_coffee | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| abo_B07124WCZY | abo | armchair | no style both judges name: qwen ['modern', 'scandinavian', 'japandi', 'minimal'], glm ['classic', 'neutral'] |
| abo_B071DQRXDR | abo | mirror | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B071DZHLXH | abo | bookshelf | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| abo_B071H75K71 | abo | bed_single | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| abo_B071J7Q9X4 | abo | armchair | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 20 of 36 accepted armchair models (keep 20; its styles modern had 5 each in the first pass) |
| abo_B072M1WJ8S | abo | sofa | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 19 of 38 accepted sofa models (keep 20; its styles modern minimal, modern had 5 each in the first pass) |
| abo_B072ZK885L | abo | nightstand | front not agreed (judges and geometry or the documented front): judges: view 1 (+X); documented front -Y (ABO convention (3dmodels/README.md): glTF +Z points to the product's natural front = -Y in the importer's Z-up frame) |
| abo_B0735CKFJK | abo | bookshelf | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B0735SLC3P | abo | rug | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 21 of 22 accepted rug models (keep 20; its styles modern minimal, minimal, neutral had 5 each in the first pass) |
| abo_B07374C6R9 | abo | floor_lamp | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| abo_B073NZGLR7 | abo | wall_art | front not agreed (judges and geometry or the documented front): judges: view 2 (+Y); documented front -Y (ABO convention (3dmodels/README.md): glTF +Z points to the product's natural front = -Y in the importer's Z-up frame) |
| abo_B073NZT573 | abo | wall_art | photoreal quality below 4 (a judge): qwen 5, glm 3 |
| abo_B073NZT5CF | abo | wall_art | no style both judges name: qwen ['modern minimal', 'minimal', 'japandi', 'scandinavian'], glm ['neutral'] |
| abo_B073P14C3L | abo | wall_art | no style both judges name: qwen ['modern minimal', 'minimal', 'modern', 'japandi', 'scandinavian', 'neutral'], glm ['classic'] |
| abo_B073P19TKF | abo | wall_art | front not agreed (judges and geometry or the documented front): judges: view 2 (+Y); documented front -Y (ABO convention (3dmodels/README.md): glTF +Z points to the product's natural front = -Y in the importer's Z-up frame) |
| abo_B073P1N3GJ | abo | wall_art | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| abo_B073WQ8JLT | abo | bed_single | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B073WR5DGC | abo | bed_double | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| abo_B073WRLNS9 | abo | bed_double | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| abo_B0742D9X4R | abo | floor_lamp | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 16 of 33 accepted floor_lamp models (keep 20; its styles modern minimal, minimal, modern had 5 each in the first pass) |
| abo_B0742DJS8J | abo | floor_lamp | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 20 of 33 accepted floor_lamp models (keep 20; its styles modern minimal, modern had 5 each in the first pass) |
| abo_B075HR7KVR | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm False |
| abo_B075HR7LFF | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm False |
| abo_B075HR7LHQ | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm False |
| abo_B075HXHKZ4 | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm False |
| abo_B075HXMH4H | abo | wall_art | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| abo_B075QDGZX7 | abo | bed_double | no style both judges name: qwen ['classic'], glm ['modern', 'neutral'] |
| abo_B075X4HZV6 | abo | armchair | no style both judges name: qwen ['classic'], glm ['neutral'] |
| abo_B075Z6YRWQ | abo | tv_unit | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 23 of 23 accepted tv_unit models (keep 20; its styles japandi, modern minimal, minimal, modern had 5 each in the first pass) |
| abo_B075ZGY571 | abo | rug | no style both judges name: qwen ['modern', 'minimal', 'scandinavian', 'japandi', 'neutral'], glm ['classic', 'rustic'] |
| abo_B0772KHYF7 | abo | mirror | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| abo_B077NZFT6C | abo | dresser | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B078JG4N1G | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm True |
| abo_B078JGHZSZ | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm True |
| abo_B078JMJC49 | abo | vase | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 23 of 24 accepted vase models (keep 20; its styles modern had 5 each in the first pass) |
| abo_B079TXCC1J | abo | nightstand | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| abo_B079TYF1GK | abo | wardrobe | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B079X4Z6QX | abo | dresser | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| abo_B07B4CZP32 | abo | armchair | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 17 of 36 accepted armchair models (keep 20; its styles modern had 5 each in the first pass) |
| abo_B07B4DBBPG | abo | sofa | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 23 of 38 accepted sofa models (keep 20; its styles modern minimal, modern had 5 each in the first pass) |
| abo_B07B4SDWVF | abo | rug | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| abo_B07B4SDZ7T | abo | rug | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 22 of 22 accepted rug models (keep 20; its styles modern minimal, minimal, neutral had 5 each in the first pass) |
| abo_B07B51946F | abo | table_lamp | not the decor type (a judge; a planter must hold a plant): qwen False, glm False |
| abo_B07B7GYMQ9 | abo | tv_unit | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 21 of 23 accepted tv_unit models (keep 20; its styles modern minimal had 5 each in the first pass) |
| abo_B07B7GZTNR | abo | bookshelf | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 20 of 24 accepted bookshelf models (keep 20; its styles modern minimal had 5 each in the first pass) |
| abo_B07B82PXCW | abo | table_dining | not the furniture type (a judge): qwen False, glm True |
| abo_B07B87J7L3 | abo | table_dining | not the furniture type (a judge): qwen False, glm True |
| abo_B07B8MTV4L | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm False |
| abo_B07B8P1JGF | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm False |
| abo_B07BMQXWX1 | abo | cushion | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 21 of 23 accepted cushion models (keep 20; its styles neutral had 5 each in the first pass) |
| abo_B07BMTXJ1V | abo | cushion | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 20 of 23 accepted cushion models (keep 20; its styles neutral had 5 each in the first pass) |
| abo_B07BMTXJ6B | abo | cushion | no style both judges name: qwen ['modern minimal', 'minimal', 'modern'], glm ['neutral'] |
| abo_B07BMTXRR1 | abo | cushion | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 23 of 23 accepted cushion models (keep 20; its styles scandinavian, neutral had 5 each in the first pass) |
| abo_B07BWMSM1J | abo | armchair | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 19 of 36 accepted armchair models (keep 20; its styles modern had 5 each in the first pass) |
| abo_B07D4F6ZKH | abo | chair | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 22 of 38 accepted chair models (keep 20; its styles modern had 5 each in the first pass) |
| abo_B07DBB7831 | abo | nightstand | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| abo_B07DBB7FVP | abo | nightstand | no style both judges name: qwen ['modern minimal', 'minimal', 'modern'], glm ['classic', 'rustic'] |
| abo_B07DBCN3KB | abo | floor_lamp | no style both judges name: qwen ['classic'], glm ['modern', 'industrial'] |
| abo_B07DBDMN5F | abo | table_coffee | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| abo_B07DBDX1P2 | abo | armchair | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 30 of 36 accepted armchair models (keep 20; its styles modern had 5 each in the first pass) |
| abo_B07DBF3VJY | abo | table_coffee | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B07DBG898G | abo | sofa | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 21 of 38 accepted sofa models (keep 20; its styles modern minimal, modern had 5 each in the first pass) |
| abo_B07DBHCKKS | abo | table_lamp | no style both judges name: qwen ['classic'], glm ['scandinavian', 'neutral'] |
| abo_B07DBHM1SZ | abo | floor_lamp | no style both judges name: qwen ['classic'], glm ['modern', 'industrial'] |
| abo_B07DMHTGJD | abo | bookshelf | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| abo_B07DTLKL7L | abo | table_lamp | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| abo_B07DVVKD85 | abo | nightstand | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| abo_B07DYV7WN2 | abo | chair | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 18 of 38 accepted chair models (keep 20; its styles modern had 5 each in the first pass) |
| abo_B07F49VHB8 | abo | table_coffee | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 22 of 33 accepted table_coffee models (keep 20; its styles minimal, modern had 5 each in the first pass) |
| abo_B07FK69CKR | abo | armchair | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 15 of 36 accepted armchair models (keep 20; its styles modern had 5 each in the first pass) |
| abo_B07G527L5S | abo | table_coffee | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 25 of 33 accepted table_coffee models (keep 20; its styles modern minimal, minimal, modern had 5 each in the first pass) |
| abo_B07GFFPKFV | abo | wardrobe | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B07GFRCLMN | abo | desk | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 21 of 26 accepted desk models (keep 20; its styles scandinavian, modern minimal, minimal, modern had 5 each in the first pass) |
| abo_B07GFSJ69T | abo | wardrobe | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B07GFWW5JZ | abo | desk | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B07H8SKPWP | abo | nightstand | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B07H8SSJVW | abo | dresser | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B07HK3F2GG | abo | floor_lamp | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 23 of 33 accepted floor_lamp models (keep 20; its styles modern minimal, minimal, modern had 5 each in the first pass) |
| abo_B07HKGHTGF | abo | table_lamp | no style both judges name: qwen ['modern minimal', 'minimal', 'modern'], glm ['scandinavian', 'neutral'] |
| abo_B07HSK9SVW | abo | mirror | not the decor type (a judge; a planter must hold a plant): qwen False, glm True |
| abo_B07HSKBHBT | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm False |
| abo_B07HSKY884 | abo | bookshelf | no style both judges name: qwen ['industrial'], glm ['modern minimal', 'minimal', 'modern'] |
| abo_B07HSLG6WN | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm False |
| abo_B07HZ1M12W | abo | sofa | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 15 of 38 accepted sofa models (keep 20; its styles modern had 5 each in the first pass) |
| abo_B07HZ6SC9H | abo | sofa | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 24 of 38 accepted sofa models (keep 20; its styles modern minimal, modern had 5 each in the first pass) |
| abo_B07HZ6VT4D | abo | sofa | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 16 of 38 accepted sofa models (keep 20; its styles modern minimal, modern had 5 each in the first pass) |
| abo_B07HZ6X7ZK | abo | sofa | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 18 of 38 accepted sofa models (keep 20; its styles modern had 5 each in the first pass) |
| abo_B07J1YW3YT | abo | table_coffee | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 26 of 33 accepted table_coffee models (keep 20; its styles scandinavian, japandi, modern minimal, minimal, modern had 5 each in the first pass) |
| abo_B07JGMW8DG | abo | wardrobe | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B07JGY5LPJ | abo | wardrobe | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B07JLBDT51 | abo | vase | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 22 of 24 accepted vase models (keep 20; its styles scandinavian, modern minimal, minimal, modern had 5 each in the first pass) |
| abo_B07JM1H7RS | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm False |
| abo_B07JWP2Y5K | abo | dresser | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| abo_B07K6N3TNH | abo | desk | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B07K7K8YF9 | abo | chair | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 28 of 38 accepted chair models (keep 20; its styles minimal, modern had 5 each in the first pass) |
| abo_B07K7SJWCH | abo | table_dining | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 19 of 26 accepted table_dining models (keep 20; its styles scandinavian, japandi, modern minimal, minimal, modern had 5 each in the first pass) |
| abo_B07K8V2SX3 | abo | armchair | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 28 of 36 accepted armchair models (keep 20; its styles modern minimal, minimal, modern had 5 each in the first pass) |
| abo_B07M6PHS9P | abo | chair | no style both judges name: qwen ['classic'], glm ['scandinavian', 'modern', 'neutral'] |
| abo_B07M6PKM8K | abo | chair | no style both judges name: qwen ['modern minimal', 'minimal', 'modern'], glm ['classic', 'neutral'] |
| abo_B07MBFCRD8 | abo | chair | no style both judges name: qwen ['classic'], glm ['scandinavian', 'modern', 'neutral'] |
| abo_B07MBFDL34 | abo | chair | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 25 of 38 accepted chair models (keep 20; its styles scandinavian, modern minimal, minimal had 5 each in the first pass) |
| abo_B07MBFDWNM | abo | floor_lamp | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 18 of 33 accepted floor_lamp models (keep 20; its styles modern minimal, minimal, modern had 5 each in the first pass) |
| abo_B07MF1V33V | abo | table_dining | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 20 of 26 accepted table_dining models (keep 20; its styles scandinavian, minimal, modern had 5 each in the first pass) |
| abo_B07ML7PPZC | abo | floor_lamp | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 21 of 33 accepted floor_lamp models (keep 20; its styles modern minimal, minimal, modern had 5 each in the first pass) |
| abo_B07PNHSR4G | abo | bookshelf | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B07PPNNCM2 | abo | bookshelf | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B07PXFVNXR | abo | dresser | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B07PYKLXGB | abo | dresser | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B07PYT7NZ9 | abo | desk | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 22 of 26 accepted desk models (keep 20; its styles modern minimal had 5 each in the first pass) |
| abo_B07Q44L76B | abo | armchair | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 29 of 36 accepted armchair models (keep 20; its styles modern had 5 each in the first pass) |
| abo_B07QB8L7YC | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm False |
| abo_B07QC84LTR | abo | desk | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B07QD6ZDDH | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm False |
| abo_B07QD6ZV9Q | abo | vase | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 19 of 24 accepted vase models (keep 20; its styles modern minimal, minimal had 5 each in the first pass) |
| abo_B07QFB4LWJ | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm False |
| abo_B07QFB5H65 | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm False |
| abo_B07QGFYLLM | abo | side_table | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 21 of 23 accepted side_table models (keep 20; its styles japandi, modern minimal, minimal, industrial had 5 each in the first pass) |
| abo_B07QGG6C74 | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm False |
| abo_B07QHKQMYL | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm False |
| abo_B07QHL2D4B | abo | vase | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 24 of 24 accepted vase models (keep 20; its styles modern minimal, minimal, modern had 5 each in the first pass) |
| abo_B07QM1WB1J | abo | bed_single | not the furniture type (a judge): qwen False, glm False |
| abo_B07QTB45S5 | abo | bookshelf | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| abo_B07QTD914H | abo | chair | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 27 of 38 accepted chair models (keep 20; its styles scandinavian, modern minimal, minimal, modern had 5 each in the first pass) |
| abo_B07QTKCKVB | abo | desk | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B07R6TND49 | abo | bed_single | front not agreed (judges and geometry or the documented front): judges: view 2 (+Y); documented front -Y (ABO convention (3dmodels/README.md): glTF +Z points to the product's natural front = -Y in the importer's Z-up frame) |
| abo_B07R7XFD22 | abo | bed_double | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| abo_B07R8WD99Z | abo | table_coffee | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 23 of 33 accepted table_coffee models (keep 20; its styles modern minimal, minimal had 5 each in the first pass) |
| abo_B07RMZ8B11 | abo | tv_unit | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| abo_B07RVBMJB8 | abo | side_table | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 22 of 23 accepted side_table models (keep 20; its styles scandinavian, modern minimal, minimal, modern had 5 each in the first pass) |
| abo_B07TF9MY62 | abo | chair | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 20 of 38 accepted chair models (keep 20; its styles modern minimal, modern had 5 each in the first pass) |
| abo_B07ZVLRCSG | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm False |
| abo_B07ZVM6QMT | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm False |
| abo_B07ZVMQ9B9 | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm False |
| abo_B0824DVF9J | abo | floor_lamp | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 15 of 33 accepted floor_lamp models (keep 20; its styles modern minimal, modern had 5 each in the first pass) |
| abo_B0824F3KWB | abo | floor_lamp | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 22 of 33 accepted floor_lamp models (keep 20; its styles minimal, modern had 5 each in the first pass) |
| abo_B0824F7ZLF | abo | floor_lamp | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 13 of 33 accepted floor_lamp models (keep 20; its styles minimal, modern had 5 each in the first pass) |
| abo_B0825D7RYW | abo | floor_lamp | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 24 of 33 accepted floor_lamp models (keep 20; its styles modern minimal, minimal, modern had 5 each in the first pass) |
| abo_B082VSLQBK | abo | side_table | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 23 of 23 accepted side_table models (keep 20; its styles modern minimal, minimal, modern had 5 each in the first pass) |
| abo_B082VSXML3 | abo | table_dining | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| abo_B082VT4GGJ | abo | side_table | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| abo_B083YFL4D7 | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm True |
| abo_B083YFL9JB | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm False |
| abo_B083YFPZ7X | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm False |
| abo_B083YFS2FR | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm False |
| abo_B084DQ4YVX | abo | mirror | no style both judges name: qwen ['scandinavian', 'japandi', 'modern minimal', 'minimal', 'modern', 'neutral'], glm ['classic', 'rustic'] |
| abo_B084HV6KDL | abo | mirror | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| abo_B084KD18YS | abo | mirror | no style both judges name: qwen ['modern minimal', 'minimal', 'modern'], glm ['classic', 'neutral'] |
| abo_B084QWW4LR | abo | tv_unit | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 22 of 23 accepted tv_unit models (keep 20; its styles japandi, modern minimal, modern had 5 each in the first pass) |
| abo_B084T7MQB4 | abo | chair | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 26 of 38 accepted chair models (keep 20; its styles scandinavian, modern minimal, minimal, modern had 5 each in the first pass) |
| abo_B084W2DDSG | abo | chair | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 19 of 38 accepted chair models (keep 20; its styles modern minimal, minimal, modern had 5 each in the first pass) |
| abo_B084ZB8Z79 | abo | bed_double | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| abo_B0853Q3Z93 | abo | table_dining | not the furniture type (a judge): qwen False, glm True |
| abo_B085FGSHQH | abo | armchair | no style both judges name: qwen ['classic'], glm ['neutral'] |
| abo_B086VLRYXS | abo | bed_single | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| abo_B086VNNCMZ | abo | bed_double | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| adf60e42de904d3abb1d45d3ae2c20ec | objaverse | washbasin | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry undecided (back_taller: offsets -0.148 (x) and +0.137 (y) do not single out one axis) |
| aedb9509ef9347a5b055e02deeadeff7 | objaverse | armchair | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 22 of 36 accepted armchair models (keep 20; its styles classic had 5 each in the first pass) |
| b0c0c9c65d06443c87391134a62e2287 | objaverse | table_coffee | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 30 of 33 accepted table_coffee models (keep 20; its styles japandi, modern minimal, minimal, modern had 5 each in the first pass) |
| b10785bcfc6e46a080614293c3ff6e1c | objaverse | stove | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| b1155b5ebd7c478bb0d35747c2211e5f | objaverse | sofa | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 33 of 38 accepted sofa models (keep 20; its styles modern minimal, minimal, modern had 5 each in the first pass) |
| b2fefa6f7af04c18966655d68a458974 | objaverse | armchair | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 36 of 36 accepted armchair models (keep 20; its styles classic had 5 each in the first pass) |
| b7f753028d354b419de1dcd966ab9f60 | objaverse | table_dining | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| b8792d1b3acf4081b0f173497d19d08b | objaverse | bookshelf | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry undecided (open_side: panel fractions {'-x': 0.0104, '+x': 0.0218, '-y': 0.0002, '+y': 0.0238} give 0 axes with one closed side) |
| b8c382798cdf473b86ed497a34770b35 | objaverse | chair | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 34 of 38 accepted chair models (keep 20) |
| b930438e1f804c409fd9c3f5e4b01628 | objaverse | desk | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 24 of 26 accepted desk models (keep 20; its styles modern minimal, minimal, modern had 5 each in the first pass) |
| baded4f3a22e4d6e9472e925e6f1fc12 | objaverse | bookshelf | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| bcab82613d3844aaba5d7049cedc5104 | objaverse | stove | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| bcfae6acaa254778921933e9ca0f52b9 | objaverse | table_dining | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 26 of 26 accepted table_dining models (keep 20; its styles scandinavian, modern minimal, minimal, modern had 5 each in the first pass) |
| bd384d46514548cf8c4202f1ae6ea551 | objaverse | fridge | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| be0c2264afaa496f9d2c4f09c528f14f | objaverse | table_dining | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 25 of 26 accepted table_dining models (keep 20; its styles scandinavian, japandi, modern minimal, minimal, modern had 5 each in the first pass) |
| be45901e180640f6881fdcf189994873 | objaverse | bathtub | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| c11f517d18d4494c8907c5a8f78f45a7 | objaverse | sofa | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| c1338e44401949c1be64e6668d38c100 | objaverse | potted_plant | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| c1cbd15423b74c1a84517e6bc331d15f | objaverse | armchair | no style both judges name: qwen ['modern', 'minimal', 'scandinavian', 'japandi'], glm ['neutral'] |
| c42d069236174467a2fb536f7d42d7f0 | objaverse | table_coffee | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 27 of 33 accepted table_coffee models (keep 20; its styles japandi, modern minimal, minimal, modern had 5 each in the first pass) |
| c46c5299740346a2b0a3c778cdcc140e | objaverse | stove | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| c4a92f9eafa64e03b8fe6e1c4ce462ab | objaverse | potted_plant | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| c5da9821e5684103bf0e6897c5c69b1e | objaverse | desk | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| c603a9922c6a4e77ab2306590f536ad6 | objaverse | armchair | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 33 of 36 accepted armchair models (keep 20; its styles modern minimal, minimal, modern had 5 each in the first pass) |
| c626625486104768a6cab5eb4ecf9cf3 | objaverse | potted_plant | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| c66f09a20a9146ab9b004685a5a93787 | objaverse | desk | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| c67f61fa444044bcb88ec3e28f0ca7ac | objaverse | desk | front not agreed (judges and geometry or the documented front): judges: qwen 1, glm 3 |
| c6a248430aff4543aaa0e87b968c617a | objaverse | wardrobe | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry +Y |
| c7d79c5a304a476d87c8014a2f6565cf | objaverse | desk | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry +X |
| c83fd12998524dcab47e8127bb22dc00 | objaverse | stove | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry +Y |
| ce421f10e46d415198d5d19c5bd265f2 | objaverse | bookshelf | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| d0f8edca337b43338674ca392f36c4df | objaverse | wardrobe | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| d16f72508d29424d972da569a9551d11 | objaverse | fridge | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry -X |
| d1d7750af5144d1bb7d9fcc66b137c4c | objaverse | bed_single | front not agreed (judges and geometry or the documented front): judges: qwen 2, glm 0 |
| d26b667147a34c90b70fbeee399499fb | objaverse | wardrobe | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry undecided (detail_side: vertex counts {'-x': 3974, '+x': 4010, '-y': 2480, '+y': 2117} give no side with 1.3x more detail) |
| d367f2a1e96644c7afd46fdd47659a69 | objaverse | wardrobe | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry undecided (detail_side: vertex counts {'-x': 851, '+x': 848, '-y': 95, '+y': 111} give no side with 1.3x more detail) |
| d584a1c6840949a8bad9d55e527e219b | objaverse | chair | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 38 of 38 accepted chair models (keep 20) |
| d601c2907f114376bf9826272d686e81 | objaverse | chair | front not agreed (judges and geometry or the documented front): judges: view 2 (+Y); geometry undecided (back_taller: offsets -0.167 (x) and -0.296 (y) do not single out one axis) |
| d7fcaa3e8c844418a38b721c325bb2af | objaverse | bed_single | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| db46661c8a714905853e38ca88e0e971 | objaverse | toilet | front not agreed (judges and geometry or the documented front): judges: qwen 1, glm 3 |
| db56721845f441d9841c82b31cfb71f8 | objaverse | stove | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| dc16ef2fe078419fa8eae914c06d2080 | objaverse | potted_plant | not the furniture type (a judge): qwen False, glm True |
| dcd691724f6b4d29a6d16def24d14e6e | objaverse | bathtub | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry +Y |
| dda2613eb5c04527a325a3b0bce9f79c | objaverse | bed_single | front not agreed (judges and geometry or the documented front): judges: view 1 (+X); geometry undecided (back_taller: top centroid offset -0.006 of the extent on y is below 0.08: no taller side) |
| dfb7c3b51e264b5083dc28450e55c2a0 | objaverse | chair | front not agreed (judges and geometry or the documented front): judges: qwen 0, glm 3 |
| dfea434382554526b04635013a59f13e | objaverse | washbasin | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| e1ebf58bb90d4ea6b2a9643bfef9ecf8 | objaverse | floor_lamp | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 29 of 33 accepted floor_lamp models (keep 20; its styles classic had 5 each in the first pass) |
| e49d29f9a6f94a8cb62ca0a8e1cc1bfe | objaverse | toilet | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry undecided (back_taller: offsets +0.155 (x) and +0.301 (y) do not single out one axis) |
| e4a1aafed0ec43a79c20f91dfcfe5670 | objaverse | stove | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| e9edbd0c027c4f648e1405df96670cc1 | objaverse | toilet | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| e9f40d803a874e84931192f09dedd58b | objaverse | desk | front not agreed (judges and geometry or the documented front): judges: view 3 (-X); geometry +Y |
| ea1ea4d5847b4550bc58ef4107df6f94 | objaverse | fridge | front not agreed (judges and geometry or the documented front): judges: qwen 1, glm 0 |
| ea5d7b8656c74af3843a5fcb34c30d21 | objaverse | bed_double | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| eadfe8fe43124205b2551635252f9e8c | objaverse | potted_plant | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| eb8faa54b7684e18abe6af39e1526b7b | objaverse | wardrobe | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| ebe62ed6dd9b446a9c9b7d7d6a8086e7 | objaverse | fridge | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| ebed0a3af94242a6be6bf0f8ed6cd49d | objaverse | armchair | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 32 of 36 accepted armchair models (keep 20; its styles modern had 5 each in the first pass) |
| ed62e8ab9bd241038609d48a26388b16 | objaverse | desk | not a single object (a judge): qwen False, glm True |
| ef3832963ab24d129ec88fd4cac4818f | objaverse | sofa | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 27 of 38 accepted sofa models (keep 20; its styles modern had 5 each in the first pass) |
| f04d12dd1e5444109f860c78679fafc0 | objaverse | armchair | no style both judges name: qwen ['classic'], glm ['neutral'] |
| f05a25da4b2c4e8d889db888cd3b2efe | objaverse | bathtub | front not agreed (judges and geometry or the documented front): judges: qwen 0, glm 2 |
| f0ff385edd4f4a9ebac56d755c2f6634 | objaverse | sofa | front not agreed (judges and geometry or the documented front): judges: qwen 1, glm 3 |
| f1b05ddf1b634481903e353d41b6a654 | objaverse | bathtub | front not agreed (judges and geometry or the documented front): judges: view 1 (+X); geometry -X |
| f2b3a71f48d040069fb144f76a1180d9 | objaverse | bed_double | not the furniture type (a judge): qwen False, glm True |
| f4a50b61cf154b01a184c117a27ec348 | objaverse | floor_lamp | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 31 of 33 accepted floor_lamp models (keep 20; its styles classic had 5 each in the first pass) |
| f57bb579c5da4b9c95f1cb874ec558f7 | objaverse | fridge | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| f7f99449b896488fa6d468e70518b21d | objaverse | armchair | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 31 of 36 accepted armchair models (keep 20; its styles modern had 5 each in the first pass) |
| f83cfd9e3edf4b4abab5ca14b0b28ec5 | objaverse | fridge | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| fd612e2ea8e94d80ac3b8097eb2e5bbe | objaverse | bathtub | front not agreed (judges and geometry or the documented front): judges: qwen 2, glm 3 |
| fe4339a62a544ec081d23f85e1a8c7f7 | objaverse | stove | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| fe63d70a5f5145788cb9b1e3c47ac3c2 | objaverse | washbasin | front not agreed (judges and geometry or the documented front): judges: qwen 2, glm 0 |
| gen_bathtub_classic_1_32213a1e | generated | bathtub | no style both judges name: qwen ['classic'], glm ['modern', 'minimal'] |
| gen_bathtub_japandi_2_c40f5efc | generated | bathtub | front not agreed (judges and geometry or the documented front): judges: qwen None, glm 3 |
| gen_bathtub_rustic_1_b85f8cca | generated | bathtub | front not agreed (judges and geometry or the documented front): judges: qwen 2, glm 0 |
| gen_bathtub_scandinavian_3_057a7982 | generated | bathtub | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| gen_bowl_classic_1_9ed1c80b | generated | bowl | no style both judges name: qwen ['modern minimal', 'minimal', 'scandinavian', 'japandi'], glm ['classic', 'neutral'] |
| gen_fridge_classic_1_24a6ed0f | generated | fridge | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| gen_fridge_minimal_1_131f791b | generated | fridge | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| gen_fridge_modern_1_0f715b05 | generated | fridge | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| gen_fridge_scandinavian_2_5eb44a0e | generated | fridge | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| gen_fridge_scandinavian_3_4b9294cb | generated | fridge | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| gen_fridge_scandinavian_4_4b9bb6e4 | generated | fridge | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| gen_potted_plant_classic_1_a5ff1adf | generated | potted_plant | no style both judges name: qwen ['modern minimal', 'minimal', 'modern'], glm ['japandi', 'neutral'] |
| gen_potted_plant_industrial_1_fb22f191 | generated | potted_plant | no style both judges name: qwen ['modern minimal', 'minimal', 'modern', 'scandinavian', 'japandi'], glm ['neutral'] |
| gen_shower_classic_1_e26e5e0a | generated | shower | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| gen_shower_japandi_2_b6c31e9a | generated | shower | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| gen_shower_japandi_3_2c7b7e7d | generated | shower | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| gen_shower_modern_1_1cb8199a | generated | shower | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| gen_shower_modern_2_707d4703 | generated | shower | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| gen_shower_modern_3_37941d2f | generated | shower | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| gen_shower_modern_minimal_1_d787862a | generated | shower | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| gen_shower_modern_minimal_2_dab54bc3 | generated | shower | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| gen_shower_modern_minimal_3_5108e5ad | generated | shower | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| gen_shower_scandinavian_2_88469e91 | generated | shower | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| gen_shower_scandinavian_3_2d3b69d4 | generated | shower | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| gen_shower_scandinavian_4_31320d88 | generated | shower | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| gen_sink_kitchen_classic_1_f7bbb88f | generated | sink_kitchen | no style both judges name: qwen ['classic'], glm ['modern minimal', 'minimal', 'modern'] |
| gen_sink_kitchen_industrial_1_15bcc635 | generated | sink_kitchen | front not agreed (judges and geometry or the documented front): judges: qwen 2, glm 0 |
| gen_sink_kitchen_minimal_1_2e90ac4a | generated | sink_kitchen | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| gen_sink_kitchen_modern_3_eb304e4d | generated | sink_kitchen | front not agreed (judges and geometry or the documented front): judges: qwen 0, glm 2 |
| gen_sink_kitchen_modern_minimal_2_d36a47fa | generated | sink_kitchen | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| gen_sink_kitchen_modern_minimal_3_e95e2f4d | generated | sink_kitchen | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| gen_stove_mediterranean_1_f0595767 | generated | stove | no style both judges name: qwen ['classic'], glm ['modern', 'neutral'] |
| gen_toilet_classic_1_f4cb8d97 | generated | toilet | front not agreed (judges and geometry or the documented front): judges: qwen 1, glm 0 |
| gen_toilet_japandi_2_0697e750 | generated | toilet | front not agreed (judges and geometry or the documented front): judges: qwen 3, glm 0 |
| gen_toilet_modern_1_3cae74e3 | generated | toilet | front not agreed (judges and geometry or the documented front): judges: qwen 1, glm 0 |
| gen_toilet_modern_minimal_1_c0ee88fc | generated | toilet | front not agreed (judges and geometry or the documented front): judges: qwen 3, glm 0 |
| gen_toilet_scandinavian_1_f4f34056 | generated | toilet | front not agreed (judges and geometry or the documented front): judges: qwen 3, glm 0 |
| gen_toilet_scandinavian_2_21c43147 | generated | toilet | front not agreed (judges and geometry or the documented front): judges: qwen 3, glm 0 |
| gen_toilet_scandinavian_3_c526dae1 | generated | toilet | front not agreed (judges and geometry or the documented front): judges: qwen 3, glm 0 |
| gen_wardrobe_japandi_1_c9a57dbb | generated | wardrobe | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 19 of 22 accepted wardrobe models (keep 20; its styles scandinavian, modern minimal, minimal, modern had 5 each in the first pass) |
| gen_wardrobe_mediterranean_1_dce90b0a | generated | wardrobe | over the per-type limit of the catalogue (20 per type, docs/milestone9.md §1): rank 22 of 22 accepted wardrobe models (keep 20; its styles scandinavian, modern minimal, minimal, modern had 5 each in the first pass) |
| gen_washbasin_japandi_4_576e4361 | generated | washbasin | front not agreed (judges and geometry or the documented front): judges: qwen 0, glm 1 |
| ikcAlbZ2YXxyKWW3r4iOMRW9qR2 | objaverse | bathtub | photoreal quality below 4 (a judge): qwen 3, glm 4 |
