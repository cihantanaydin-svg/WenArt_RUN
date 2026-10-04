# Furniture library (docs/milestone7.md §7, docs/milestone8.md §2)

Contains information from Objaverse 1.0 (https://huggingface.co/datasets/allenai/objaverse, revision 21e4e14), which is made available under the ODC Attribution License (ODC-By 1.0, https://opendatacommons.org/licenses/by/1-0/). Every object keeps its own licence, as declared by its uploader and not verified by WenArt_RUN (CC0 1.0 and CC BY 4.0 unflagged, every other licence flagged: docs/milestone8.md §2): check it before commercial use. This file is licensed ODC-By 1.0, not MIT.

Contains 3D models and product data from Amazon Berkeley Objects (https://amazon-berkeley-objects.s3.amazonaws.com/index.html), (c) Amazon.com, licensed CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Credit for the data, including all images and 3D models: Amazon.com; for building the dataset: Matthieu Guillaumin, Thomas Dideriksen, Kenan Deng, Himanshu Arora (Amazon.com), Jasmine Collins and Jitendra Malik (UC Berkeley). Changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched.

Objaverse: [allenai/objaverse](https://huggingface.co/datasets/allenai/objaverse) @ `21e4e14` (ODC-By-1.0). Licence strings and metadata field names of objaverse.yaml verified on the pod: yes. Every licence is taken (docs/milestone8.md §2); not CC0 / CC BY 4.0 -> licence_flag.

## Sources

| Source | Survey file | Candidates | With GLB | Ready | Judged by both | Accepted | In catalogue |
|---|---|---|---|---|---|---|---|
| abo | survey_abo.json | 436 | 436 | 436 | 436 | 148 | 148 |
| objaverse | survey.json | 303 | 303 | 256 | 256 | 38 | 38 |

## Steps

| Step | Objects |
|---|---|
| Objaverse: LVIS objects in the mapped categories | 1498 |
| Objaverse: licence CC0 or CC BY 4.0 (metadata) | 1370 |
| Objaverse: other licences (taken, flagged) | 128 |
| Objaverse: past the metadata prefilter (credit, faces, size) | 924 |
| Candidates of every source (downloaded; textured or vertex-coloured) | 739 |
| Rendered (thumbnails) | 739 |
| Ready for judging (unit and type resolved) | 692 |
| of which normalised by type (model units unknown) | 153 |
| Judged by both models | 692 |
| Accepted | 186 |
| In catalog_library.json | 186 |

## Per type (Objaverse bed candidates are split into bed_single / bed_double after the unit guess)

| Type | Source | LVIS | Candidates | Ready | Accepted | In catalogue |
|---|---|---|---|---|---|---|
| armchair | abo | – | 24 | 24 | 10 | 10 |
| armchair | objaverse | 97 | 24 | 21 | 2 | 2 |
| bathtub | objaverse | 30 | 14 | 8 | 0 | 0 |
| bed_double | abo | – | 24 | 24 | 8 | 8 |
| bed_double | objaverse | – | 0 | 11 | 1 | 1 |
| bed_double|bed_single | objaverse | 53 | 22 | 0 | 0 | 0 |
| bed_single | abo | – | 12 | 12 | 7 | 7 |
| bed_single | objaverse | – | 0 | 11 | 1 | 1 |
| bookshelf | abo | – | 24 | 24 | 6 | 6 |
| bookshelf | objaverse | 103 | 24 | 20 | 5 | 5 |
| chair | abo | – | 24 | 24 | 9 | 9 |
| chair | objaverse | 453 | 24 | 21 | 3 | 3 |
| cushion | abo | – | 24 | 24 | 5 | 5 |
| desk | abo | – | 24 | 24 | 8 | 8 |
| desk | objaverse | 76 | 24 | 20 | 0 | 0 |
| dresser | abo | – | 24 | 24 | 10 | 10 |
| floor_lamp | abo | – | 24 | 24 | 9 | 9 |
| floor_lamp | objaverse | 79 | 21 | 15 | 3 | 3 |
| fridge | objaverse | 55 | 15 | 13 | 3 | 3 |
| nightstand | abo | – | 24 | 24 | 5 | 5 |
| plant | abo | – | 24 | 24 | 0 | 0 |
| potted_plant | objaverse | 81 | 24 | 23 | 6 | 6 |
| rug | abo | – | 24 | 24 | 11 | 11 |
| side_table | abo | – | 24 | 24 | 12 | 12 |
| sofa | abo | – | 24 | 24 | 11 | 11 |
| sofa | objaverse | 81 | 24 | 18 | 1 | 1 |
| stove | objaverse | 35 | 12 | 9 | 1 | 1 |
| table_coffee | abo | – | 24 | 24 | 7 | 7 |
| table_coffee | objaverse | 51 | 18 | 16 | 2 | 2 |
| table_dining | abo | – | 24 | 24 | 9 | 9 |
| table_dining | objaverse | 70 | 16 | 10 | 1 | 1 |
| toilet | objaverse | 111 | 13 | 13 | 3 | 3 |
| tv_unit | abo | – | 24 | 24 | 9 | 9 |
| wall_art | abo | – | 24 | 24 | 8 | 8 |
| wardrobe | abo | – | 16 | 16 | 4 | 4 |
| wardrobe | objaverse | 97 | 24 | 23 | 3 | 3 |
| washbasin | objaverse | 26 | 4 | 4 | 3 | 3 |

## Refusals by reason (first failed rule per object)

| Step | Code | Reason | Objects | Sources |
|---|---|---|---|---|
| survey | face_count | face count outside 2k-150k | 545 | objaverse 545 |
| survey | glb_size | GLB larger than the source's limit (Objaverse 40 MB, ABO 60 MB) | 53 | abo 24, objaverse 29 |
| survey | size_range | box outside the resolved type's size range (units known: never normalised) | 520 | abo 520 |
| survey | untextured | no image texture and no vertex colours | 204 | objaverse 204 |
| survey | not_selected | below the candidates per type (rank, or the pick order) | 4342 |  |
| thumbnails | unit_none | no unit factor fits and the box proportions (footprint, height / width) are outside the type's ranges | 47 | objaverse 47 |
| accept | front_not_agreed | front not agreed (judges and geometry or the documented front) | 62 | abo 4, objaverse 58 |
| accept | no_common_style | no style both judges name | 20 | abo 15, objaverse 5 |
| accept | not_decor_type | not the decor type (a judge; a planter must hold a plant) | 24 | abo 24 |
| accept | not_single | not a single object (a judge) | 2 | objaverse 2 |
| accept | over_style_limit | every style family it fits already has 3 models of its type | 234 | abo 179, objaverse 55 |
| accept | over_type_limit | over the per-type limit of the catalogue | 40 | abo 13, objaverse 27 |
| accept | quality | photoreal quality below 4 (a judge) | 111 | abo 49, objaverse 62 |
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
| armchair | 580 | 560 | 24 | 528 |
| bed_double | 161 | 144 | 24 | 120 |
| bed_single | 27 | 12 | 12 | 0 |
| bookshelf | 48 | 41 | 24 | 17 |
| chair | 430 | 367 | 24 | 342 |
| cushion | 195 | 195 | 24 | 168 |
| desk | 146 | 101 | 24 | 77 |
| dresser | 53 | 46 | 24 | 22 |
| floor_lamp | 101 | 76 | 24 | 52 |
| nightstand | 82 | 76 | 24 | 52 |
| plant | 189 | 142 | 24 | 118 |
| rug | 861 | 861 | 24 | 834 |
| side_table | 136 | 121 | 24 | 97 |
| sofa | 962 | 748 | 24 | 715 |
| table_coffee | 152 | 143 | 24 | 119 |
| table_dining | 54 | 46 | 24 | 22 |
| tv_unit | 68 | 57 | 24 | 33 |
| wall_art | 639 | 633 | 24 | 609 |
| wardrobe | 21 | 16 | 16 | 0 |

Product types with a 3D model left unmapped: HOME_FURNITURE_AND_DECOR 389, STOOL_SEATING 340, OTTOMAN 288, LAMP 244, HEADBOARD 206, LIGHT_FIXTURE 195, TABLE 161, CHAIR 132, HOME 121, CABINET 112, HOME_MIRROR 109, PILLOW 88, SHELF 57, VASE 50, BENCH 39, FURNITURE_COVER 34, ELECTRIC_FAN 29, SPORTING_GOODS 28, CLOTHES_RACK 24, STORAGE_BOX 23, FREESTANDING_SHELTER 20, FLAT_SCREEN_DISPLAY_MOUNT 18, CURTAIN 17, MATTRESS 17, MULTIPORT_HUB 16, PROFESSIONAL_HEALTHCARE 16, AUTO_ACCESSORY 14, BEAN_BAG_CHAIR 14, FURNITURE 14, AIR_CONDITIONER 13.

## Licence flags (catalogue)

| Licence | Flag | Models |
|---|---|---|
| CC-BY-4.0 | – | 183 |
| CC-BY-NC-4.0 | non_commercial | 2 |
| CC-BY-SA-4.0 | share_alike | 1 |

## Style coverage

Models per type and style family: library + Poly Haven (`neutral` counts for every family; beds with a mattress or as a bed frame with a deck). `–` = no model: refit builds the parametric mesh for that pair (or a generated model fills it, docs/milestone8.md §3).

| Type | scandinavian | japandi | modern minimal | minimal | modern | industrial | mediterranean | classic | rustic |
|---|---|---|---|---|---|---|---|---|---|
| bed_single | 4+0 | 3+0 | 8+0 | 6+0 | 5+0 | 1+0 | – | – | – |
| bed_double | 4+0 | 3+0 | 5+0 | 4+0 | 5+0 | 2+0 | – | 0+1 | 1+0 |
| sofa | 2+0 | – | 6+0 | 3+0 | 9+0 | – | – | 3+3 | – |
| armchair | 4+0 | 2+0 | 7+1 | 5+1 | 9+2 | 2+0 | 2+0 | 5+1 | 2+0 |
| table_dining | 6+0 | 5+0 | 7+0 | 6+0 | 6+0 | 4+0 | 1+0 | 1+0 | 3+3 |
| table_coffee | 4+0 | 6+0 | 7+0 | 6+0 | 6+2 | 5+0 | 1+0 | 2+1 | 3+1 |
| desk | 6+0 | 5+0 | 6+0 | 3+0 | 6+0 | 3+2 | – | – | 1+1 |
| chair | 4+0 | 3+0 | 4+0 | 4+0 | 6+1 | 2+0 | – | 4+1 | 2+2 |
| wardrobe | 4+0 | 1+0 | 4+0 | 4+0 | 4+0 | 1+0 | 1+0 | 4+0 | 2+0 |
| fridge | – | – | 3+0 | 2+0 | 3+0 | – | – | – | – |
| stove | 0+1 | 0+1 | 0+1 | 0+1 | 0+1 | 1+1 | 0+1 | 0+1 | 0+1 |
| washbasin | 1+0 | – | 3+0 | 3+0 | 3+0 | – | – | – | – |
| toilet | – | – | 3+0 | 3+0 | 3+0 | – | – | – | – |
| bathtub | – | – | – | – | – | – | – | – | – |
| tv_unit | 3+0 | 8+0 | 5+1 | 4+1 | 4+1 | 1+1 | – | 1+0 | 3+1 |
| bookshelf | 6+1 | 3+1 | 8+1 | 6+1 | 6+1 | 4+0 | 1+0 | 3+0 | 1+2 |
| nightstand | 3+1 | 4+1 | 4+1 | 4+1 | 3+1 | – | – | 0+1 | 2+1 |
| dresser | 5+0 | 4+0 | 7+0 | 5+0 | 7+0 | 3+0 | 2+0 | 3+2 | 3+0 |
| side_table | 4+0 | 5+0 | 6+0 | 5+0 | 4+0 | 7+0 | 2+0 | 3+0 | 5+0 |
| floor_lamp | 3+0 | – | 5+0 | 6+0 | 8+0 | 3+0 | – | 3+0 | – |
| potted_plant | – | – | 2+0 | 3+0 | 1+0 | – | 2+0 | – | 2+0 |

Parametric: 47 of 189 type/family pairs.

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
| `objaverse_6eb4212e70b941a3bd2db196a47828b9` | bed_single | objaverse | True | False | – |
| `abo_B071FJR4FW` | bed_double | abo | True | False | – |
| `abo_B071W2SCTJ` | bed_double | abo | True | False | – |
| `abo_B075QDMWTP` | bed_double | abo | True | False | – |
| `abo_B075Z8767S` | bed_double | abo | True | False | – |
| `abo_B07B4Z9Q3S` | bed_double | abo | True | False | – |
| `abo_B07BBWMPJM` | bed_double | abo | True | False | – |
| `abo_B086TGFT35` | bed_double | abo | True | False | – |
| `abo_B08FTN8KHY` | bed_double | abo | True | False | – |
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
| bed_single | objaverse | `objaverse_6eb4212e70b941a3bd2db196a47828b9` | Lowpoly Bed | Mohamed199 | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -X (high) | 4/4 | 1.11 x 1.8 x 0.691 | x0.00535266 |
| bed_double | abo | `abo_B071FJR4FW` | Amazon Brand – Stone & Beam Glenwood Industrial Metal Accent Bed, Queen, 84.5"L, Oak | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/4 | 1.63 x 2.11 x 1.42 | x1 |
| bed_double | abo | `abo_B071W2SCTJ` | Amazon Brand – Stone & Beam Glenwood Industrial Metal Accent Bed, King, 86"L, Oak | Amazon.com | CC-BY-4.0 | – | minimal, modern | -Y (high) | 5/4 | 1.76 x 2.22 x 1.49 | x1 |
| bed_double | abo | `abo_B075QDMWTP` | Amazon Brand – Rivet Payton Mid-Century Modern Tufted King Bed with Headboard, 82" W, Natural | Amazon.com | CC-BY-4.0 | – | modern minimal | -Y (high) | 5/4 | 2.04 x 2.38 x 1.52 | x1 |
| bed_double | abo | `abo_B075Z8767S` | Amazon Brand – Stone & Beam Bateman Casual Rustic Wood Platform Bed Frame with Tall Headboard, King, 81"W, Brown | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/4 | 1.7 x 2.28 x 1.42 | x1 |
| bed_double | abo | `abo_B07B4Z9Q3S` | Stone & Beam Prudence Tufted King Bed, 84"W, Spinnsol Cocoa | Amazon.com | CC-BY-4.0 | – | modern | -Y (high) | 5/5 | 1.7 x 2.39 x 1.43 | x1 |
| bed_double | abo | `abo_B07BBWMPJM` | Amazon Brand - Movian Corona Double Bed, 4 ft 6, High Foot End Bed Frame, Solid Pine Wood | Amazon.com | CC-BY-4.0 | – | scandinavian, rustic | -Y (high) | 4/4 | 1.49 x 2.07 x 1.1 | x1 |
| bed_double | abo | `abo_B086TGFT35` | AmazonBasics Solid Platform Bed - Rustic Finish - No Box Spring Needed - Strong Wood Slat Support, Queen | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/4 | 1.54 x 2.02 x 0.431 | x1 |
| bed_double | abo | `abo_B08FTN8KHY` | Amazon Brand - Solimo Senna Metal Glossy King Bed (Black) | Amazon.com | CC-BY-4.0 | – | modern minimal, industrial | -Y (high) | 4/4 | 1.88 x 2.04 x 0.94 | x1 |
| bed_double | objaverse | `objaverse_5d3a99865ac84d8a8bf06b263aa5bb55` | Old Bed | barism09 | CC-BY-4.0 | – | industrial | -Y (high) | 4/4 | 1.47 x 2.55 x 1.4 | x0.01 |
| sofa | abo | `abo_B0714QGC72` | Amazon Brand – Stone & Beam Bradbury Chesterfield Tufted Leather Sofa Couch, 92.9"W, Cognac | Amazon.com | CC-BY-4.0 | – | classic | -Y (high) | 5/5 | 2.37 x 0.989 x 0.76 | x1 |
| sofa | abo | `abo_B071J7Q3J4` | Amazon Brand – Stone & Beam Bradbury Chesterfield Tufted Sofa Couch, 92.9"W, Hemp | Amazon.com | CC-BY-4.0 | – | classic | -Y (high) | 5/5 | 2.69 x 1.08 x 0.847 | x1 |
| sofa | abo | `abo_B072555T67` | Marchio Amazon - Movian Ackan - Divano a 3 posti, 209 x 87 x 80 cm, grigio chiaro | Amazon.com | CC-BY-4.0 | – | modern minimal, modern | -Y (high) | 4/5 | 2.1 x 0.849 x 0.795 | x1 |
| sofa | abo | `abo_B075X2X4GY` | Amazon Brand – Rivet Uptown Mid-Century Velvet Tufted Customizable Daybed Sofa, 78"W, Dove Grey &amp; Brass | Amazon.com | CC-BY-4.0 | – | modern minimal, modern | -Y (high) | 4/5 | 1.98 x 0.686 x 0.635 | x1 |
| sofa | abo | `abo_B075X4JB3K` | Amazon Brand – Rivet Eva Tufted Mid-Century Velvet Down-Filled Loveseat, 60.5"W, Hunter Green | Amazon.com | CC-BY-4.0 | – | classic | -Y (high) | 5/5 | 1.54 x 0.895 x 0.768 | x1 |
| sofa | abo | `abo_B07B4FW7H5` | Amazon Brand – Stone & Beam Andover Studio Sofa Couch, 78"W, Driftwood Leather | Amazon.com | CC-BY-4.0 | – | modern minimal, modern | -Y (high) | 5/5 | 1.97 x 0.923 x 0.863 | x1 |
| sofa | abo | `abo_B07HZ5P7P9` | Amazon Brand – Stone & Beam Bagley Sectional Component, Left-Facing Loveseat, Fabric, 52"W, Linen | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 4/5 | 1.39 x 0.991 x 0.989 | x1 |
| sofa | abo | `abo_B07HZ6GJC2` | Amazon Brand – Stone & Beam Bagley Sectional Component, Right Facing Loveseat, Fabric, 52"W, Linen | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 4/5 | 1.39 x 0.991 x 0.989 | x1 |
| sofa | abo | `abo_B07HZ6HHFF` | Amazon Brand – Stone & Beam Bagley Sectional Component, Armless Loveseat, Fabric, 44"W, Linen | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 4/5 | 1.24 x 0.951 x 1.01 | x1 |
| sofa | abo | `abo_B07HZ6X7ZF` | Amazon Brand – Stone & Beam Bagley Sectional Component, Left-Facing Sofa Chaise, Fabric, 41"W, Linen | Amazon.com | CC-BY-4.0 | – | modern | -Y (high) | 5/5 | 2.24 x 1.11 x 1.03 | x1 |
| sofa | abo | `abo_B07K9PMZJL` | Amazon Brand - Movian Dyvran 3-Seater Upholstered Sofa, 197 x 83 x 83 cm, Stain-Resistant Polyester, Dust Blue | Amazon.com | CC-BY-4.0 | – | scandinavian, modern | -Y (high) | 4/4 | 1.97 x 0.83 x 0.83 | x1 |
| sofa | objaverse | `objaverse_104ac40ef3ad4dac8079a11548c470e7` | Sofa | hask191919 | CC-BY-4.0 | – | scandinavian, modern | -Y (high) | 5/5 | 3.04 x 1.07 x 1.12 | x1 |
| armchair | abo | `abo_B07124WN69` | Amazon Brand – Rivet Huxley Mid-Century Modern Accent Chair, 28.3"W, Marine Blue | Amazon.com | CC-BY-4.0 | – | scandinavian, modern | -Y (high) | 5/5 | 0.719 x 0.889 x 0.864 | x1 |
| armchair | abo | `abo_B0719WQGYJ` | Amazon Brand – Rivet Emerly Modern Living Room Chair, 41"W, Pewter | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 4/5 | 1.04 x 0.889 x 0.864 | x1 |
| armchair | abo | `abo_B072PZ4LQ2` | Amazon Brand – Rivet Emerly Modern Living Room Chair, 41"W, Ecru | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 1.04 x 0.889 x 0.865 | x1 |
| armchair | abo | `abo_B073G7BVCT` | Amazon Brand – Stone & Beam Highland Modern Wingback Living Room Accent Chair, 31.9"W, Oatmeal | Amazon.com | CC-BY-4.0 | – | neutral | -Y (high) | 5/4 | 0.764 x 0.948 x 1.08 | x1 |
| armchair | abo | `abo_B0746KJVP2` | Amazon Brand – Rivet Charlotte Mid-Century Modern Upholstered Gold Accent Chair, 29"W, Natural | Amazon.com | CC-BY-4.0 | – | modern minimal, modern | -Y (high) | 5/5 | 0.805 x 0.813 x 0.966 | x1 |
| armchair | abo | `abo_B075X467QG` | Amazon Brand – Stone & Beam Hillsboro Modern Wingback Living Room Accent Chair With Nailhead Trim, 29"W, Beige | Amazon.com | CC-BY-4.0 | – | classic | -Y (high) | 5/5 | 0.737 x 0.94 x 1.03 | x1 |
| armchair | abo | `abo_B075X4N3GM` | Amazon Brand – Rivet Aiden Tufted Mid-Century Modern Velvet Accent Chair, 35.4"W, Otter Grey | Amazon.com | CC-BY-4.0 | – | modern, neutral | -Y (high) | 5/5 | 0.928 x 0.843 x 0.773 | x1 |
| armchair | abo | `abo_B075X4N3J5` | Amazon Brand – Rivet Villain Mid-Century Modern Leather Metal Leg Accent Lounge Chair, 37.4"W, Black | Amazon.com | CC-BY-4.0 | – | modern minimal, modern | -Y (high) | 5/5 | 0.836 x 0.826 x 0.922 | x1 |
| armchair | abo | `abo_B07DBDQJRF` | Amazon Brand – Ravenna Home Hughes Curved Back Tufted Patterned Accent Chair, 25"W, Arrow | Amazon.com | CC-BY-4.0 | – | classic | -Y (high) | 5/5 | 0.686 x 0.613 x 0.859 | x1 |
| armchair | abo | `abo_B07HZ9K9PG` | Amazon Brand – Stone & Beam Calhoun Living Room Accent Chair, 42"W, Ecru | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 5/4 | 1.18 x 1.01 x 1.02 | x1 |
| armchair | objaverse | `objaverse_124297e7e4574c48b9c1b814b6ddf516` | animated_sphere | ferhatsen | CC-BY-4.0 | – | classic | -Y (high) | 5/5 | 0.751 x 0.84 x 0.91 | x1 |
| armchair | objaverse | `objaverse_b23ec9725c48494788d1d88104acbb4a` | High back Arm chair (Free Download) | dopaminecat | CC-BY-4.0 | – | scandinavian, modern | -Y (high) | 4/5 | 0.81 x 0.892 x 0.923 | x0.362583 |
| table_dining | abo | `abo_B075Z9QB7N` | Amazon Brand – Rivet Industrial Wood and Metal Round Dining Kitchen Table, 35.4"W, Recycled Elm | Amazon.com | CC-BY-4.0 | – | industrial | -Y (low) | 5/5 | 0.885 x 0.885 x 0.658 | x1 |
| table_dining | abo | `abo_B07B7BGXN9` | Amazon Brand – Stone & Beam Alejandra Casual Wood Dining Kitchen Table, 78"-98"L, Brown | Amazon.com | CC-BY-4.0 | – | rustic | -Y (low) | 4/5 | 1.97 x 1.07 x 0.793 | x1 |
| table_dining | abo | `abo_B07B82PXCM` | Amazon Brand – Stone & Beam Bradhurst Casual Farmhouse Wood Dining Kitchen Table, 61"-84"L, White | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern, rustic | -Y (low) | 5/4 | 1.5 x 0.922 x 0.743 | x1 |
| table_dining | abo | `abo_B07B82PXD8` | Amazon Brand – Rivet Ian Modern Medium Dining Kitchen Table, Expandable, 60-80"L, Brown | Amazon.com | CC-BY-4.0 | – | scandinavian, minimal, modern | -Y (low) | 5/5 | 1.4 x 0.757 x 0.76 | x1 |
| table_dining | abo | `abo_B07B82WF6G` | Amazon Brand – Rivet Mid-Century Modern Wood Round Dining Kitchen Table, 43.3"W, Beige | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (low) | 5/5 | 1.04 x 1.04 x 0.666 | x1 |
| table_dining | abo | `abo_B07H93GTHW` | Amazon Brand - Movian Kuban Dining Table, 160 x 78 x 90cm, Brown Oak-Effect Table Top/Black Legs | Amazon.com | CC-BY-4.0 | – | modern minimal, industrial | -Y (low) | 5/5 | 1.58 x 0.881 x 0.736 | x1 |
| table_dining | abo | `abo_B07K7K25NM` | Amazon Brand - Alkove Hayes Solid Wood Dining Table with Stainless Steel Base, Seats 6, 180 x 90 x 75cm, Wild Oak/Stainless Steel | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (low) | 5/5 | 1.8 x 0.9 x 0.75 | x1 |
| table_dining | abo | `abo_B07RT5JN33` | Amazon Brand Movian Kyyvesi Dining Table 120.5 x 71.4 x 76 cm Walnut Effect | Amazon.com | CC-BY-4.0 | – | modern minimal, industrial | -Y (low) | 5/5 | 1.21 x 0.714 x 0.76 | x1 |
| table_dining | abo | `abo_B0853Q71J6` | Amazon Brand – Rivet Mid-Century Modern Pine Extendable Dining Table, 39"–77"W, Brown | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (low) | 5/5 | 0.991 x 0.991 x 0.754 | x1 |
| table_dining | objaverse | `objaverse_3b4ee19c627e4fb4a3305621cf925aa2` | Dining Set | dan2211082 | CC-BY-4.0 | – | rustic, neutral | -Y (low) | 4/5 | 1.31 x 1.23 x 0.704 | x0.0077457 |
| table_coffee | abo | `abo_B072ZK885D` | Amazon Brand – Rivet Allyson Mid-Century Modern Two-Shelf Adjustable Coffee Table, Walnut | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (low) | 5/5 | 1.08 x 0.527 x 0.429 | x1 |
| table_coffee | abo | `abo_B075Z8WD59` | Amazon Brand – Rivet Hillside Antiqued Round Coffee Table, 39.4"D, Wood and Bronze | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, neutral | -Y (low) | 4/5 | 1 x 1 x 0.409 | x1 |
| table_coffee | abo | `abo_B075ZBVZPB` | Amazon Brand – Stone & Beam Larson Industrial Wood & Metal Coffee Table, 50"W, Walnut | Amazon.com | CC-BY-4.0 | – | industrial | -Y (low) | 5/5 | 0.99 x 0.452 x 0.399 | x1 |
| table_coffee | abo | `abo_B07GDMBZJJ` | Amazon Brand - Rivet Leaf-Shaped Coffee Table, 120 x 60 x 36cm, MDF with Walnut Veneer/Black Metal Base | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (low) | 5/5 | 1.2 x 0.598 x 0.36 | x1 |
| table_coffee | abo | `abo_B07GDSF3MR` | Amazon Brand - Rivet Round Coffee Table with Solid Wood Legs, 80 x 80 x 36cm, MDF with Walnut Veneer/Solid Beech Wood | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (low) | 5/5 | 0.8 x 0.8 x 0.36 | x1 |
| table_coffee | abo | `abo_B07L8DT2XT` | Phoenix Home Rustic Industrial Solid Wood and Steel Open Shelf Coffee Table, Brown | Amazon.com | CC-BY-4.0 | – | japandi, modern minimal, minimal, modern, industrial | -Y (low) | 5/4 | 1.07 x 0.61 x 0.457 | x1 |
| table_coffee | abo | `abo_B07QF9Y71V` | Amazon Brand – Stone & Beam Industrial Coffee Table, 53"W, Antique Natural and Black | Amazon.com | CC-BY-4.0 | – | modern minimal, industrial | -Y (low) | 5/4 | 1.35 x 0.75 x 0.4 | x1 |
| table_coffee | objaverse | `objaverse_01ff88bfc0034211b9f4996d620bc333` | Palette Table | Javier.Cantero | CC-BY-4.0 | – | japandi, modern minimal, minimal, modern, industrial, rustic | -Y (low) | 4/4 | 1.29 x 0.861 x 0.25 | x10.5567 |
| table_coffee | objaverse | `objaverse_f4031bb5f7e64ebca4c37d4fa5ba6e8d` | LP Table | doplerato | CC-BY-4.0 | – | classic, rustic | -Y (low) | 4/4 | 1.2 x 0.669 x 0.36 | x8.32595 |
| desk | abo | `abo_B01FK3FWNG` | Amazon Brand - Movian Haven Retro Desk with Riser, Grey Oak, 113.54 x 60.45 x 89.92 cm | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, modern | -Y (high) | 5/4 | 1.14 x 0.605 x 0.899 | x1 |
| desk | abo | `abo_B075ZBVZST` | Amazon Brand – Rivet Mid-Century Curved Wood Table Home Office Computer Desk, 48.4"L, Walnut | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, modern | -Y (high) | 5/5 | 1.26 x 0.486 x 0.8 | x1 |
| desk | abo | `abo_B07B7DFS3S` | Amazon Brand – Stone & Beam Industrial Metal Office Computer Desk, 60"W, Power Sit to Standing Table, Brown/Black | Amazon.com | CC-BY-4.0 | – | industrial, rustic | -Y (high) | 5/4 | 1.54 x 0.784 x 0.725 | x1 |
| desk | abo | `abo_B07GFT639N` | Amazon Brand - Movian Indre 1-Drawer Desk, 56 x 110 x 73cm, Light Brown/Oak Foil Finish | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 5/4 | 1.1 x 0.56 x 0.73 | x1 |
| desk | abo | `abo_B07HSCRFTN` | Amazon Brand – Rivet Mid-Century Desk - 35 Inch, Natural | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/5 | 1.19 x 0.769 x 1.06 | x1 |
| desk | abo | `abo_B07TKY3L6X` | Amazon Brand - Movian Côa 4-Drawer Desk, 160 x 73 x 77.5cm, Vintage Dark Brown Oak-Effect/Black Metal | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern, industrial | -Y (high) | 5/5 | 1.6 x 0.73 x 0.78 | x1 |
| desk | abo | `abo_B082DFL4JW` | Amazon Brand – Rivet Avery Industrial Home Office Writing Desk with Metal Base, 40"W, Chestnut Brown Finish | Amazon.com | CC-BY-4.0 | – | japandi, modern minimal, industrial | -Y (high) | 5/4 | 1.02 x 0.47 x 0.762 | x1 |
| desk | abo | `abo_B0876NZQ9C` | AmazonBasics 40" Multipurpose Foldable Computer Study Desk - Natural | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 5/4 | 1.02 x 0.508 x 0.762 | x1 |
| chair | abo | `abo_B01MQJV7ID` | AmazonBasics Sedia direzionale da ufficio con schienale alto, regolabile in altezza - Marrone | Amazon.com | CC-BY-4.0 | – | modern | -Y (high) | 5/5 | 0.662 x 0.739 x 1.11 | x1 |
| chair | abo | `abo_B0728NW8FP` | Amazon Brand – Rivet Ashworth Armless Velvet Accent Chair, 21.6"W, Navy | Amazon.com | CC-BY-4.0 | – | modern minimal, modern | -Y (high) | 5/5 | 0.521 x 0.55 x 0.805 | x1 |
| chair | abo | `abo_B07DBD9WHX` | Amazon Brand – Ravenna Home Armless Tufted Turned Wood Leg Accent Chair, 29"W, Blue | Amazon.com | CC-BY-4.0 | – | classic | -Y (high) | 5/5 | 0.74 x 0.719 x 0.77 | x1 |
| chair | abo | `abo_B07DBHCKHY` | Amazon Brand – Ravenna Home Tufted Armless English Roll Traditional Accent Chair, 26.8"W, Merlot Red | Amazon.com | CC-BY-4.0 | – | classic | -Y (high) | 5/5 | 0.582 x 0.605 x 0.75 | x1 |
| chair | abo | `abo_B07FY8PZBH` | Phoenix Home PU Leather Dining Chair Set of 2, 18.11" Length x 21.65" Width x 30.7" Height, Brown | Amazon.com | CC-BY-4.0 | – | industrial | -Y (high) | 5/5 | 0.46 x 0.551 x 0.78 | x1 |
| chair | abo | `abo_B07JK8CL2Z` | Amazon Brand - Movian Square | Amazon.com | CC-BY-4.0 | – | scandinavian, modern | -Y (high) | 5/4 | 0.57 x 0.57 x 0.78 | x1 |
| chair | abo | `abo_B07QJ24FSL` | Amazon Brand – Ravenna Home Dining Chairs, Set of 2, 40"H, Praline | Amazon.com | CC-BY-4.0 | – | classic | -Y (high) | 5/5 | 0.513 x 0.66 x 1.02 | x1 |
| chair | abo | `abo_B0857JLP6K` | Amazon Brand – Stone & Beam Modern Farmhouse Birch Dining Chair, 17.5"W, Dark Gray | Amazon.com | CC-BY-4.0 | – | minimal, industrial | -Y (high) | 4/5 | 0.45 x 0.546 x 0.991 | x1 |
| chair | abo | `abo_B0857JM2NC` | Amazon Brand – Stone & Beam Mid-Century Beech and Rattan Dining Chair with Arms, 21.9"W, Natural | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/4 | 0.556 x 0.495 x 0.762 | x1 |
| chair | objaverse | `objaverse_47a690dcecf847fca99c4f89111db85b` | Char 2 | DimaSP | CC-BY-4.0 | – | classic, rustic | -Y (high) | 4/5 | 0.462 x 0.541 x 1.01 | x0.808639 |
| chair | objaverse | `objaverse_acf6497a3d274d90ad3750510348f07a` | chare | DimaSP | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern, rustic | -Y (high) | 5/5 | 0.455 x 0.525 x 0.999 | x1 |
| chair | objaverse | `objaverse_d2785b57e7da45858f2fe8bf4dedd68d` | Chair | 杭州维界科技有限公司 | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/5 | 0.517 x 0.503 x 0.829 | x0.01 |
| wardrobe | abo | `abo_B07B3XXD3P` | Vida Designs Corona Wardrobe, 3 Door, Solid Pine Wood, Solid Pine Wood, Distressed Waxed Pine Bedroom Wooden Storage Mexican Furniture | Amazon.com | CC-BY-4.0 | – | scandinavian, rustic, neutral | -Y (high) | 4/4 | 1.5 x 0.57 x 1.87 | x1 |
| wardrobe | abo | `abo_B07GFRKNR1` | Amazon Brand - Movian Inari Modern 2-Door 2-Drawer Wardrobe, 100 x 57 x 180 cm, Light Brown Oak-Effect | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 5/4 | 0.991 x 0.577 x 1.81 | x1 |
| wardrobe | abo | `abo_B07GFS1VB6` | Amazon Brand - Movian Kolva Sliding 2-Door Wardrobe, 180 x 61 x 197cm, Light Brown Oak-Effect | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 5/5 | 1.78 x 0.629 x 1.96 | x1 |
| wardrobe | abo | `abo_B07JGPKZYT` | Amazon Brand - Movian Mira 4-Door Wardrobe with Mirrors, 181 x 207 x 58cm, Light Brown Oak-Effect | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 5/4 | 1.81 x 0.58 x 2.07 | x1 |
| wardrobe | objaverse | `objaverse_05a035c3347645b8a7ceb6d65f825ac3` | Dikkies Closet | klaxoneer | CC-BY-4.0 | – | classic | -Y (high) | 5/4 | 1.14 x 0.624 x 1.76 | x1 |
| wardrobe | objaverse | `objaverse_094697a23146463cb5564ac8bf89e5c4` | Traditional Mennonite corner cabinet | vinigor | CC-BY-NC-4.0 | non_commercial | classic | -Y (high) | 4/4 | 1.45 x 0.786 x 2.6 | x0.000995894 |
| wardrobe | objaverse | `objaverse_b3a99e956be64ab6958f7f5e1895f031` | Warn Wardrobe | seenoise | CC-BY-4.0 | – | classic, rustic | -Y (high) | 4/4 | 1.29 x 0.564 x 2.31 | x1 |
| fridge | objaverse | `objaverse_2071bda681b642218b6829b82e4fd93b` | Refrigerator - Grey Polished Metal | Glowbox 3D | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.766 x 0.661 x 1.54 | x0.193519 |
| fridge | objaverse | `objaverse_68d69bbf7a454a09a2536ac0762532f3` | Old Fridge | golddog | CC-BY-4.0 | – | modern minimal, minimal, modern | +X (high) | 4/4 | 0.725 x 0.698 x 1.09 | x0.419674 |
| fridge | objaverse | `objaverse_c9c4e705bf794cb88d5d8726095f4917` | Haier Refrigerator | cgwings | CC-BY-NC-4.0 | non_commercial | modern minimal, modern | +Y (high) | 4/4 | 0.833 x 0.918 x 1.8 | x1 |
| stove | objaverse | `objaverse_7c5c9dec5c2e4ff998c386410b0e3686` | Stove | Daniyal Malik | CC-BY-4.0 | – | industrial | -X (high) | 4/4 | 0.592 x 0.71 x 0.867 | x0.00228858 |
| washbasin | objaverse | `objaverse_3eafb89804b54c8e8cbe35e4d456e0a9` | Bathroom | Thunder | CC-BY-SA-4.0 | share_alike | modern minimal, minimal, modern | +X (high) | 4/4 | 0.949 x 0.325 x 0.516 | x0.00323813 |
| washbasin | objaverse | `objaverse_8580c4545d1649efb3503c6c2a012641` | Ingstav147 PULT ZRK V1 | KRONZI | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | +X (high) | 5/4 | 0.838 x 0.368 x 1.01 | x0.00698632 |
| washbasin | objaverse | `objaverse_ce1a06f7cbe1425099a145f851fc5dee` | Sink | Shining Salt | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.649 x 0.476 x 0.55 | x0.324323 |
| toilet | objaverse | `objaverse_0b3325fad3e740b1ac86173c90b56afd` | Toilettes | Lightningx | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.462 x 0.621 x 0.839 | x0.0146675 |
| toilet | objaverse | `objaverse_24d1b493899d407780140688abae19bc` | Toilet | Xill | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.453 x 0.633 x 0.801 | x0.744926 |
| toilet | objaverse | `objaverse_3446229dce1f47528fa871cc7669136c` | Toilet | Ali107_YT | CC-BY-4.0 | – | modern minimal, minimal, modern | +X (high) | 4/4 | 0.453 x 0.634 x 0.761 | x0.0015794 |
| tv_unit | abo | `abo_B00OGP5S98` | Home Corona 2 unità da 1 TV a schermo Piatto, supporto/ripostigli | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/5 | 1.2 x 0.4 x 0.51 | x1 |
| tv_unit | abo | `abo_B072ZNMKGM` | Amazon Brand – Rivet King Street Industrial Cabinet Media Console Table With Functional Storage, Walnut, Black Metal, Glass | Amazon.com | CC-BY-4.0 | – | japandi, modern minimal, minimal | -Y (high) | 5/4 | 1.2 x 0.399 x 0.8 | x1 |
| tv_unit | abo | `abo_B075Z8KX9N` | Amazon Brand – Stone & Beam Ferndale Rustic Reclaimed Pine Media TV Console Stand, 71"W, Sandstone | Amazon.com | CC-BY-4.0 | – | japandi, rustic | -Y (high) | 4/5 | 1.8 x 0.453 x 0.573 | x1 |
| tv_unit | abo | `abo_B07B8FN8TP` | Amazon Brand – Stone & Beam Traditional Oak Wood Media TV Console Table, 59", Walnut Finish | Amazon.com | CC-BY-4.0 | – | classic, rustic | -Y (high) | 5/5 | 1.48 x 0.461 x 0.852 | x1 |
| tv_unit | abo | `abo_B07BVHKPFS` | Amazon Brand – Rivet Bowlyn Mid-Century Modern Wood TV Media Table Stand, 64", Walnut | Amazon.com | CC-BY-4.0 | – | japandi, modern | -Y (high) | 5/5 | 1.63 x 0.48 x 0.61 | x1 |
| tv_unit | abo | `abo_B07DYV7WNN` | ROCKPOINT TV Stand, 42x16x23.6inch, Walnut Brown | Amazon.com | CC-BY-4.0 | – | japandi, rustic | -Y (high) | 4/5 | 1.07 x 0.406 x 0.813 | x1 |
| tv_unit | abo | `abo_B07HSG5DGP` | Amazon Brand – Rivet Roxmere Mid-Century Modern TV Media Console Center Stand, 59"W, Acacia Wood &amp; Dark Metal | Amazon.com | CC-BY-4.0 | – | japandi, modern minimal, industrial | -Y (high) | 5/5 | 1.48 x 0.454 x 0.506 | x1 |
| tv_unit | abo | `abo_B07K6VT8VN` | Movian TV Board for TVs up to 80 Inches | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/4 | 1.9 x 0.42 x 0.537 | x1 |
| tv_unit | abo | `abo_B07VHNMRY8` | Amazon Brand - Movian 2-Door 1-Shelf TV Stand, 176 x 40 x 58 cm, White and Oak Effect | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/4 | 1.76 x 0.4 x 0.58 | x1 |
| bookshelf | abo | `abo_B075Z6YS1Z` | Amazon Brand – Stone & Beam Larson Industrial Wood and Metal 4-Shelf Bookcase, 73"H, Walnut | Amazon.com | CC-BY-4.0 | – | industrial | -Y (high) | 5/4 | 0.874 x 0.359 x 1.86 | x1 |
| bookshelf | abo | `abo_B07B7J2VCD` | Amazon Brand – Stone & Beam Casual Wood Bookcase, 34"W, Natural Rattan | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 5/4 | 0.864 x 0.453 x 1.93 | x1 |
| bookshelf | abo | `abo_B07H8P1N9T` | Amazon Brand - Movian Moselle 2-Door Cabinet/Bookcase with 8 Shelves, 139 x 100 x 45cm, Light Brown Oak-Effect/White | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 5/4 | 1 x 0.45 x 1.39 | x1 |
| bookshelf | abo | `abo_B07HSCNKCT` | Stone & Beam Rylee Modern Bookcase 39.4"Wx76.8”H, Mixed Gray | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/4 | 0.748 x 0.307 x 1.47 | x1 |
| bookshelf | abo | `abo_B07JGY5LNV` | Amazon Brand - Alkove Velle Bookcase, 42 x 95 x 202cm, Oiled Honey Oak | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/5 | 0.95 x 0.42 x 2.02 | x1 |
| bookshelf | abo | `abo_B07QC876WJ` | Amazon Brand – Rivet Davenport Contemporary Shelf, 34"W, Elm and Metal | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, industrial | -Y (high) | 5/4 | 0.874 x 0.386 x 1.8 | x1 |
| bookshelf | objaverse | `objaverse_4939d1bca386405f9cc22c48441b63de` | Bookcase | Bec | CC-BY-4.0 | – | modern minimal, industrial | -Y (high) | 5/4 | 0.999 x 0.502 x 1.28 | x1 |
| bookshelf | objaverse | `objaverse_68baafb344b2445a8e7f4917b6fe8a63` | Scaffale B | Francesco Coldesina | CC-BY-4.0 | – | classic | -Y (high) | 5/4 | 1.16 x 0.392 x 1.84 | x0.0069429 |
| bookshelf | objaverse | `objaverse_6c5ac2547db34c3c81b2e4808b000386` | Dusty Old Bookshelf (FREE) | Brandon Westlake | CC-BY-4.0 | – | classic | +Y (high) | 4/4 | 0.92 x 0.387 x 2.08 | x1 |
| bookshelf | objaverse | `objaverse_b43c45317fd74a4aa9ba443b9a355ea3` | Bookcase | Icanreed | CC-BY-4.0 | – | modern, neutral | -Y (high) | 5/4 | 1.05 x 0.434 x 1.92 | x0.348837 |
| bookshelf | objaverse | `objaverse_eb98251fbccf4cdd8a3737362e2378e9` | Solo 100シェルフ WN | classe-saga | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 5/5 | 0.965 x 0.29 x 1.04 | x1 |
| nightstand | abo | `abo_B01D3C7Z4A` | Amazon Brand - Hallowood Waverly 1 Drawer Small Side Table in Light Oak Finish | Solid Wooden End/Lamp Stand/Bedside Cabinet/Nightstand, (WAV-LAM590) | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/5 | 0.428 x 0.418 x 0.614 | x1 |
| nightstand | abo | `abo_B075X38PZ7` | Amazon Brand – Stone & Beam Newport Nightstand End Table, 22"W, Toffee Oak | Amazon.com | CC-BY-4.0 | – | rustic | -Y (high) | 5/5 | 0.586 x 0.461 x 0.597 | x1 |
| nightstand | abo | `abo_B07K7K7GTZ` | Amazon Brand - Alkove Hayes 1-Drawer Solid Wood Nightstand, 56 x 44 x 47cm, Wild Oak | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/5 | 0.56 x 0.44 x 0.47 | x1 |
| nightstand | abo | `abo_B07VB7Q6W7` | Amazon Brand - Movian Kyyvesi, 2-Drawer Storage Night Stand, 60 x 42 x 50 cm, Walnut Effect | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/5 | 0.6 x 0.42 x 0.5 | x1 |
| nightstand | abo | `abo_B084MYDTKM` | Amazon Brand - Rivet Mango Wood and Iron 3-Drawer Shutter Nightstand, 18"W, Natural Finish | Amazon.com | CC-BY-4.0 | – | japandi, modern minimal, minimal, rustic | -Y (high) | 5/5 | 0.457 x 0.406 x 0.559 | x1 |
| dresser | abo | `abo_B00838756S` | Vida Designs Corona Merchant Chest Of Drawers, 9 Drawer, Solid Pine Wood | Amazon.com | CC-BY-4.0 | – | rustic, neutral | -Y (high) | 4/4 | 0.99 x 0.41 x 0.74 | x1 |
| dresser | abo | `abo_B009S7IZWG` | Amazon Brand - Movian Corona Sideboard, 1 Door 4 Drawer, Solid Pine Wood, 76 x 86 x 40 cm | Amazon.com | CC-BY-4.0 | – | rustic | -Y (high) | 4/4 | 0.915 x 0.44 x 0.835 | x1 |
| dresser | abo | `abo_B01MG6BPC6` | Vida Designs Corona Chest Of Drawers, 4 Drawer, Rustic, Solid Pine Wood. | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 4/4 | 0.8 x 0.41 x 0.73 | x1 |
| dresser | abo | `abo_B071FJR3S6` | Amazon Brand – Stone & Beam Glenwood Industrial Metal Dresser, 60"W, Oak | Amazon.com | CC-BY-4.0 | – | modern minimal | -Y (high) | 5/5 | 1.65 x 0.623 x 1.06 | x1 |
| dresser | abo | `abo_B071FJR479` | Amazon Brand – Rivet West, Mid-Century, Oak Distinct Grain, 6-Drawer Dresser, 60"W, Dark Oak Finish | Amazon.com | CC-BY-4.0 | – | modern minimal, modern | -Y (high) | 5/4 | 1.52 x 0.512 x 0.889 | x1 |
| dresser | abo | `abo_B071P9WJBT` | Amazon Brand – Stone & Beam Parson 6-Drawer Wood Bedroom Dresser, 60"W, Natural | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern, rustic, neutral | -Y (high) | 5/5 | 1.66 x 0.564 x 0.932 | x1 |
| dresser | abo | `abo_B075YZYJQN` | Amazon Brand – Rivet Eastport Industrial Wood Dresser, 30"W, Oak Finish | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/5 | 0.761 x 0.479 x 1.24 | x1 |
| dresser | abo | `abo_B07B4VXZZC` | Amazon Brand – Stone & Beam Gould Contemporary Wood Bedroom Dresser Chest, 18", Washed Navy and Gold | Amazon.com | CC-BY-4.0 | – | classic | -Y (high) | 4/4 | 1.05 x 0.463 x 0.986 | x1 |
| dresser | abo | `abo_B07FFWSBBF` | Artum Hill BE6-802 Laurel Dresser, 5-Drawer, Modern Gray | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 5/4 | 1.02 x 0.457 x 1.22 | x1 |
| dresser | abo | `abo_B07HSH4WFB` | Amazon Brand – Rivet Modern Chest of Drawers with Diamond Pattern, 17.7 Inch Width, Natural | Amazon.com | CC-BY-4.0 | – | modern, industrial | -Y (high) | 5/4 | 0.923 x 0.453 x 0.801 | x1 |
| side_table | abo | `abo_B072ZKPK7J` | Amazon Brand – Rivet Mid-Century Modern Round Black Wood Nesting Side End Table, 15.7" W, Dark Oak | Amazon.com | CC-BY-4.0 | – | modern minimal | -Y (low) | 5/5 | 0.399 x 0.399 x 0.46 | x1 |
| side_table | abo | `abo_B075Z8627Z` | Amazon Brand – Stone & Beam Larson Industrial Wood & Metal Side End Table, 27"W, Walnut | Amazon.com | CC-BY-4.0 | – | industrial, rustic | -Y (low) | 5/5 | 0.678 x 0.524 x 0.613 | x1 |
| side_table | abo | `abo_B075Z8KX91` | Amazon Brand – Stone & Beam Ferndale Rustic Reclaimed Pine Side End Table, 24"W, Sandstone | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, rustic | -Y (low) | 5/5 | 0.61 x 0.61 x 0.457 | x1 |
| side_table | abo | `abo_B075Z8TDQ6` | Amazon Brand – Stone & Beam Modern Rustic Reclaimed Elm Round Accent Side End Table, 16.9"W, Natural | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, minimal, modern, neutral | -Y (low) | 5/5 | 0.432 x 0.431 x 0.46 | x1 |
| side_table | abo | `abo_B075ZBW1QM` | Stone & Beam Larson Industrial Wood & Metal Side End Table, 22"W, Set of 2, Walnut | Amazon.com | CC-BY-4.0 | – | industrial, rustic | -Y (low) | 5/5 | 0.548 x 0.553 x 0.482 | x1 |
| side_table | abo | `abo_B07DB92DKW` | Amazon Brand – Ravenna Home Aubree Mid-Century Modern Shelf Storage Side Table, 23.6"W, Grey pine | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, industrial | -Y (low) | 5/5 | 0.3 x 0.599 x 0.701 | x1 |
| side_table | abo | `abo_B07H2J7689` | Ball & Cast End Table | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern, rustic, neutral | -Y (low) | 5/4 | 0.66 x 0.559 x 0.635 | x1 |
| side_table | abo | `abo_B07HSCRGTJ` | Amazon Brand – Stone & Beam 2-Tier Rustic Accent End Table, 26"W, Light Wood and Dark Metal | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern, industrial | -Y (low) | 5/5 | 0.629 x 0.628 x 0.684 | x1 |
| side_table | abo | `abo_B07M6PKCM3` | Amazon Brand – Ravenna Home Damask-Pattern Ceramic Garden Stool or Side Table, 16"H, Grey | Amazon.com | CC-BY-4.0 | – | classic | -Y (low) | 5/4 | 0.309 x 0.309 x 0.397 | x1 |
| side_table | abo | `abo_B07MBFDHRY` | Amazon Brand – Ravenna Home Clover-Pattern Ceramic Garden Stool or Side Table, 16"H, Grey | Amazon.com | CC-BY-4.0 | – | modern | -Y (low) | 5/5 | 0.352 x 0.349 x 0.387 | x1 |
| side_table | abo | `abo_B07MF1TQYR` | Amazon Brand – Ravenna Home Moroccan-Pattern Ceramic Garden Stool or Side Table, 16"H, Grey | Amazon.com | CC-BY-4.0 | – | japandi | -Y (low) | 5/5 | 0.325 x 0.325 x 0.388 | x1 |
| side_table | abo | `abo_B07QGFZ2B4` | Amazon Brand – Rivet Industrial Mango-Topped Side Table, 19.61"W | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, industrial | -Y (low) | 5/5 | 0.499 x 0.498 x 0.55 | x1 |
| floor_lamp | abo | `abo_B07374K536` | Amazon Brand – Rivet Caden Adjustable Task Floor Lamp with Bulb, 60"H, Black and Brass | Amazon.com | CC-BY-4.0 | – | modern, industrial | -Y (low) | 5/4 | 0.235 x 0.618 x 1.63 | x1 |
| floor_lamp | abo | `abo_B07374SBFN` | Amazon Brand – Stone & Beam Glass Column Brass Floor Lamp, With Bulb, Linen Shade, 13.0" x 13.0" x 59.0", Brushed Brass | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (low) | 4/5 | 0.42 x 0.42 x 1.48 | x1 |
| floor_lamp | abo | `abo_B073P25SXR` | Rivet Mid-Century Modern Theory 5-Arm Living Room Floor Lamp with Edison Light Bulbs, 60"H, Black and Brass Finish | Amazon.com | CC-BY-4.0 | – | industrial | -Y (low) | 5/4 | 0.599 x 0.572 x 1.72 | x1 |
| floor_lamp | abo | `abo_B073P3S1NX` | Rivet Olive 4 Wood Shelf Standing Floor Lamp With Light Bulb and USB Charging Station - 11.8 x 11.8 x 62 Inches, Brass | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (low) | 4/4 | 0.31 x 0.308 x 1.57 | x1 |
| floor_lamp | abo | `abo_B07B4ZK8BR` | Amazon Brand – Rivet Mid-Century Modern Floor Lamp with Wireless USB Port Charging Wood Table, 59"H, Light Bulb Included, Black | Amazon.com | CC-BY-4.0 | – | scandinavian, minimal, modern | -Y (low) | 5/4 | 0.573 x 0.573 x 1.52 | x1 |
| floor_lamp | abo | `abo_B07DBHCKML` | Amazon Brand – Ravenna Home Traditional Standing Floor Lamp with Reading Light and LED Light Bulb - 69.75 Inches, Brushed Nickel with Frosted Glass | Amazon.com | CC-BY-4.0 | – | modern | -Y (low) | 5/4 | 0.575 x 0.406 x 1.79 | x1 |
| floor_lamp | abo | `abo_B07DBK7KKZ` | Amazon Brand – Ravenna Home Frosted Glass Living Room Standing Floor Lamp with LED Light Bulb - 69.75 Inches, Brushed Nickel | Amazon.com | CC-BY-4.0 | – | classic | -Y (low) | 4/5 | 0.406 x 0.406 x 1.77 | x1 |
| floor_lamp | abo | `abo_B07HKF59YX` | Amazon Brand – Stone & Beam Mid-Century Modern Henley Living Room Standing Floor Lamp with LED Light Bulb - 15 x 15 x 58 Inches, Matte Black and Antique Brass | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (low) | 5/5 | 0.404 x 0.404 x 1.52 | x1 |
| floor_lamp | abo | `abo_B0824FJCWG` | Amazon Brand – Ravenna Home Traditional Metal Floor Lamp with Stacked Oval Accents, LED Bulb Included, 58.5"H, Polished Nickel | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (low) | 4/5 | 0.356 x 0.356 x 1.49 | x1 |
| floor_lamp | objaverse | `objaverse_0eba4ad785674d3586aafc82854100fa` | lamp | anish_ | CC-BY-4.0 | – | classic | -Y (low) | 4/5 | 0.585 x 0.61 x 1.2 | x0.0434402 |
| floor_lamp | objaverse | `objaverse_53409613b45b42b98b979f12ab8faa12` | low poly Lamp 3d model | mohamedvfx | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (low) | 4/4 | 0.518 x 0.518 x 1.2 | x0.00427403 |
| floor_lamp | objaverse | `objaverse_71853da424aa4b208e14f6cf430339ae` | Street lights | U-like | CC-BY-4.0 | – | industrial, classic | -Y (low) | 5/4 | 0.349 x 0.349 x 2.1 | x1.74412 |
| potted_plant | objaverse | `objaverse_41e58efcf647494483f9860df99acf60` | Empty Flower Pot | dumerlot | CC-BY-4.0 | – | mediterranean, rustic | -Y (low) | 4/5 | 0.598 x 0.602 x 0.487 | x2.0673 |
| potted_plant | objaverse | `objaverse_57972124483145b4a4bbf4fd4caca6e7` | succulent | Elif Smbl | CC-BY-4.0 | – | modern minimal, minimal | -Y (low) | 4/4 | 0.617 x 0.583 x 0.612 | x0.240114 |
| potted_plant | objaverse | `objaverse_71b53eaee72e4a829a9256a7bcfb7dab` | Cacti pot | Spacyy | CC-BY-4.0 | – | rustic | -Y (low) | 4/4 | 0.222 x 0.234 x 0.305 | x0.0254 |
| potted_plant | objaverse | `objaverse_9dd44cda400c48a083ffd9480067f04f` | Succulent | mika.rr | CC-BY-4.0 | – | modern minimal, minimal | -Y (low) | 4/5 | 0.497 x 0.497 x 0.512 | x0.0254 |
| potted_plant | objaverse | `objaverse_b99c584dd11d4691b5d13303383371e5` | FlowerPot | ibrahmcingi | CC-BY-4.0 | – | mediterranean | -Y (low) | 4/4 | 0.6 x 0.6 x 0.58 | x0.0027579 |
| potted_plant | objaverse | `objaverse_bf122cd0854e422bb94704552c64810b` | CGT 116 Wk8 Plant | mlin234 | CC-BY-4.0 | – | minimal, modern | -Y (low) | 4/4 | 0.238 x 0.261 x 0.361 | x0.0254 |
| cushion | abo | `abo_B074VLRP5T` | Amazon Brand – Rivet Velvet Texture Decorative Throw Pillow, 17" x 17", Midnight | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern, neutral | -Y (low) | 5/5 | 0.432 x 0.246 x 0.414 | x1 |
| cushion | abo | `abo_B079TXJV32` | Amazon Brand – Stone & Beam Mojave-Inspired Decorative Throw Pillow Cover, 20" x 20", Black and Red | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern, neutral | -Y (low) | 5/5 | 0.503 x 0.182 x 0.506 | x1 |
| cushion | abo | `abo_B079V39VG5` | Amazon Brand – Stone & Beam Transitional Woven Diamond Decorative Throw Pillow, 20" x 20", Indigo | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern, neutral | -Y (low) | 5/5 | 0.435 x 0.148 x 0.428 | x1 |
| cushion | abo | `abo_B079V3WDY9` | Amazon Brand – Stone & Beam Transitional Woven Diamond Decorative Throw Pillow Cover, 20" x 20", Indigo | Amazon.com | CC-BY-4.0 | – | scandinavian, neutral | -Y (low) | 5/5 | 0.511 x 0.162 x 0.503 | x1 |
| cushion | abo | `abo_B079V3YG6X` | Amazon Brand – Rivet Modern Geometric Decorative Print Pillow Cover, 20" x 20", Black | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (low) | 5/4 | 0.517 x 0.158 x 0.508 | x1 |
| rug | abo | `abo_B0714MJKX2` | Amazon Brand – Rivet Shaggy Short Rug, 7'7" x 9'7", Ivory | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern, neutral | -Y (low) | 4/5 | 2.53 x 2.01 x 0.0477 | x1 |
| rug | abo | `abo_B0714MJLTB` | Amazon Brand – Stone & Beam Mid-Century Modern Dusk Wool Rug, 5' x 8', Tan | Amazon.com | CC-BY-4.0 | – | classic | -Y (low) | 5/4 | 2.44 x 1.53 x 0.0104 | x1 |
| rug | abo | `abo_B0719STF79` | Amazon Brand – Rivet Diamond Trellis Tassel Wool Rug, 7'6" x 9'6", Ivory | Amazon.com | CC-BY-4.0 | – | scandinavian, neutral | -Y (low) | 4/4 | 3.22 x 2.34 x 0.0262 | x1 |
| rug | abo | `abo_B0735RHGTB` | Amazon Brand – Stone & Beam Swirling Paisley Farmhouse Motif Wool Runner Rug, 2' 6" x 8', Multi | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, neutral | -Y (low) | 4/4 | 2.68 x 0.763 x 0.0149 | x1 |
| rug | abo | `abo_B07B4SDLJM` | Amazon Brand – Rivet Contemporary Striated Jute Area Rug, 10' 6" x 8', Oatmeal | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (low) | 4/4 | 3.2 x 2.43 x 0.045 | x1 |
| rug | abo | `abo_B07B4WH5LV` | Amazon Brand – Rivet Contemporary Striated Jute Area Rug, 5' 9" x 3' 9", Silver Birch | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern, neutral | -Y (low) | 4/4 | 1.77 x 1.15 x 0.0213 | x1 |
| rug | abo | `abo_B07B4WKQHJ` | Amazon Brand – Rivet Contemporary Striated Jute Area Rug, 10' 6" x 8', Off White | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal | -Y (low) | 5/4 | 3.24 x 2.47 x 0.0456 | x1 |
| rug | abo | `abo_B07B515Q7D` | Amazon Brand – Rivet Contemporary Striated Jute Rug, 10' 6" x 8', Citron | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal | -Y (low) | 4/4 | 3.2 x 2.43 x 0.0159 | x1 |
| rug | abo | `abo_B07HSDXLX2` | Stone & Beam Rug, 3'11" x 5'11", Blue, Navy, Multicolor | Amazon.com | CC-BY-4.0 | – | classic | -Y (low) | 5/4 | 1.78 x 1.18 x 0.0121 | x1 |
| rug | abo | `abo_B07HSF7LWP` | Stone & Beam Polypropylene Round Rug, 5'3" x 5'3", Gray, Orange, Multicolor | Amazon.com | CC-BY-4.0 | – | classic | -Y (low) | 5/5 | 1.6 x 1.6 x 0.0096 | x1 |
| rug | abo | `abo_B07TS7ZCVM` | Amazon Basics - 4'X6' Plush Diamond Trellis Shag Rug, Grey | Amazon.com | CC-BY-4.0 | – | neutral | -Y (low) | 5/4 | 1.78 x 1.22 x 0.03 | x1 |
| wall_art | abo | `abo_B073NZTB8J` | Amazon Brand – Stone & Beam Modern Red and Gold Tulip Print on Canvas, Brown Frame, 13.75" x 13.75" | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 5/4 | 0.349 x 0.0381 x 0.349 | x1 |
| wall_art | abo | `abo_B073P16J69` | Amazon Brand – Rivet World Map Hemisphere Print in Black and White Vintage Wall Art, Black Frame, 30.5" x 30.5" | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal | -Y (high) | 5/4 | 0.773 x 0.0313 x 0.775 | x1 |
| wall_art | abo | `abo_B073P1H7CF` | Black and White Vintage Bike Print in White Frame, 15" x 21" | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 5/4 | 0.332 x 0.0152 x 0.477 | x1 |
| wall_art | abo | `abo_B073P5KYG9` | Amazon Brand – Stone & Beam Abstract Topographic Print in Black Wood Frame, 20" x 20" | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal, modern | -Y (high) | 5/4 | 0.507 x 0.0379 x 0.507 | x1 |
| wall_art | abo | `abo_B073P5L2QM` | Amazon Brand – Rivet Modern White Framed Black and White Paris Map Print, 30" x 30" | Amazon.com | CC-BY-4.0 | – | modern minimal, minimal | -Y (high) | 5/4 | 0.758 x 0.0375 x 0.758 | x1 |
| wall_art | abo | `abo_B073P5MPW9` | Amazon Brand – Stone & Beam Modern Turquoise and Orange Palm Print in Gray Frame Wall Art, 12" x 12" | Amazon.com | CC-BY-4.0 | – | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/4 | 0.304 x 0.0377 x 0.303 | x1 |
| wall_art | abo | `abo_B073P6FYT4` | Amazon Brand – Rivet Vintage Blue Yellow and Green Chairs in Gold Wood Frame Wall Art, 20" x 20" | Amazon.com | CC-BY-4.0 | – | scandinavian, modern minimal, minimal, modern | -Y (high) | 5/4 | 0.505 x 0.0371 x 0.505 | x1 |
| wall_art | abo | `abo_B07HSGM25V` | Amazon Brand – Stone & Beam Traditional Landscape Print with Copper Leaf Wall Art Decor on Canvas - 35" x 35" | Amazon.com | CC-BY-4.0 | – | neutral | -Y (high) | 4/4 | 0.888 x 0.0354 x 0.897 | x1 |

## Attribution

Contains information from Objaverse 1.0 (https://huggingface.co/datasets/allenai/objaverse, revision 21e4e14), which is made available under the ODC Attribution License (ODC-By 1.0, https://opendatacommons.org/licenses/by/1-0/). Every object keeps its own licence, as declared by its uploader and not verified by WenArt_RUN (CC0 1.0 and CC BY 4.0 unflagged, every other licence flagged: docs/milestone8.md §2): check it before commercial use. This file is licensed ODC-By 1.0, not MIT.

Contains 3D models and product data from Amazon Berkeley Objects (https://amazon-berkeley-objects.s3.amazonaws.com/index.html), (c) Amazon.com, licensed CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). Credit for the data, including all images and 3D models: Amazon.com; for building the dataset: Matthieu Guillaumin, Thomas Dideriksen, Kenan Deng, Himanshu Arora (Amazon.com), Jasmine Collins and Jitendra Malik (UC Berkeley). Changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched.

- "Amazon Brand - Movian Aveyron Single Bed Frame, 195 x 100 x 80cm, Pink" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "AmazonBasics Foldable, 14" Metal Platform Bed Frame with Tool-Free Assembly, No Box Spring Needed - Twin" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "AmazonBasics Faux Leather Upholstered Platform Bed Frame with Wooden Slats, Twin" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Movian Moselle." by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Movian Moselle." by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Modern Solid Pine Wood Platform Bed, Twin, 38.39"W, Antique Espresso" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "AmazonBasics Metal Bed with Modern Industrial Design Headboard - 14 Inch Height for Under-Bed Storage - Wood Slats - Easy Assemble, Twin" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Lowpoly Bed" by Mohamed199 (https://sketchfab.com/3d-models/6eb4212e70b941a3bd2db196a47828b9), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Glenwood Industrial Metal Accent Bed, Queen, 84.5"L, Oak" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Glenwood Industrial Metal Accent Bed, King, 86"L, Oak" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Payton Mid-Century Modern Tufted King Bed with Headboard, 82" W, Natural" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Bateman Casual Rustic Wood Platform Bed Frame with Tall Headboard, King, 81"W, Brown" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Stone & Beam Prudence Tufted King Bed, 84"W, Spinnsol Cocoa" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian Corona Double Bed, 4 ft 6, High Foot End Bed Frame, Solid Pine Wood" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "AmazonBasics Solid Platform Bed - Rustic Finish - No Box Spring Needed - Strong Wood Slat Support, Queen" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Solimo Senna Metal Glossy King Bed (Black)" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Old Bed" by barism09 (https://sketchfab.com/3d-models/5d3a99865ac84d8a8bf06b263aa5bb55), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Bradbury Chesterfield Tufted Leather Sofa Couch, 92.9"W, Cognac" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Bradbury Chesterfield Tufted Sofa Couch, 92.9"W, Hemp" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Marchio Amazon - Movian Ackan - Divano a 3 posti, 209 x 87 x 80 cm, grigio chiaro" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Uptown Mid-Century Velvet Tufted Customizable Daybed Sofa, 78"W, Dove Grey &amp; Brass" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Eva Tufted Mid-Century Velvet Down-Filled Loveseat, 60.5"W, Hunter Green" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Andover Studio Sofa Couch, 78"W, Driftwood Leather" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Bagley Sectional Component, Left-Facing Loveseat, Fabric, 52"W, Linen" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Bagley Sectional Component, Right Facing Loveseat, Fabric, 52"W, Linen" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Bagley Sectional Component, Armless Loveseat, Fabric, 44"W, Linen" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Bagley Sectional Component, Left-Facing Sofa Chaise, Fabric, 41"W, Linen" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian Dyvran 3-Seater Upholstered Sofa, 197 x 83 x 83 cm, Stain-Resistant Polyester, Dust Blue" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Sofa" by hask191919 (https://sketchfab.com/3d-models/104ac40ef3ad4dac8079a11548c470e7), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Huxley Mid-Century Modern Accent Chair, 28.3"W, Marine Blue" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Emerly Modern Living Room Chair, 41"W, Pewter" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Emerly Modern Living Room Chair, 41"W, Ecru" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Highland Modern Wingback Living Room Accent Chair, 31.9"W, Oatmeal" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Charlotte Mid-Century Modern Upholstered Gold Accent Chair, 29"W, Natural" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Hillsboro Modern Wingback Living Room Accent Chair With Nailhead Trim, 29"W, Beige" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Aiden Tufted Mid-Century Modern Velvet Accent Chair, 35.4"W, Otter Grey" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Villain Mid-Century Modern Leather Metal Leg Accent Lounge Chair, 37.4"W, Black" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Ravenna Home Hughes Curved Back Tufted Patterned Accent Chair, 25"W, Arrow" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Calhoun Living Room Accent Chair, 42"W, Ecru" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "animated_sphere" by ferhatsen (https://sketchfab.com/3d-models/124297e7e4574c48b9c1b814b6ddf516), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "High back Arm chair (Free Download)" by dopaminecat (https://sketchfab.com/3d-models/b23ec9725c48494788d1d88104acbb4a), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Industrial Wood and Metal Round Dining Kitchen Table, 35.4"W, Recycled Elm" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Alejandra Casual Wood Dining Kitchen Table, 78"-98"L, Brown" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Bradhurst Casual Farmhouse Wood Dining Kitchen Table, 61"-84"L, White" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Ian Modern Medium Dining Kitchen Table, Expandable, 60-80"L, Brown" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Mid-Century Modern Wood Round Dining Kitchen Table, 43.3"W, Beige" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian Kuban Dining Table, 160 x 78 x 90cm, Brown Oak-Effect Table Top/Black Legs" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Alkove Hayes Solid Wood Dining Table with Stainless Steel Base, Seats 6, 180 x 90 x 75cm, Wild Oak/Stainless Steel" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand Movian Kyyvesi Dining Table 120.5 x 71.4 x 76 cm Walnut Effect" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Mid-Century Modern Pine Extendable Dining Table, 39"–77"W, Brown" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Dining Set" by dan2211082 (https://sketchfab.com/3d-models/3b4ee19c627e4fb4a3305621cf925aa2), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Allyson Mid-Century Modern Two-Shelf Adjustable Coffee Table, Walnut" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Hillside Antiqued Round Coffee Table, 39.4"D, Wood and Bronze" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Larson Industrial Wood & Metal Coffee Table, 50"W, Walnut" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Rivet Leaf-Shaped Coffee Table, 120 x 60 x 36cm, MDF with Walnut Veneer/Black Metal Base" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Rivet Round Coffee Table with Solid Wood Legs, 80 x 80 x 36cm, MDF with Walnut Veneer/Solid Beech Wood" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Phoenix Home Rustic Industrial Solid Wood and Steel Open Shelf Coffee Table, Brown" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Industrial Coffee Table, 53"W, Antique Natural and Black" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Palette Table" by Javier.Cantero (https://sketchfab.com/3d-models/01ff88bfc0034211b9f4996d620bc333), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "LP Table" by doplerato (https://sketchfab.com/3d-models/f4031bb5f7e64ebca4c37d4fa5ba6e8d), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian Haven Retro Desk with Riser, Grey Oak, 113.54 x 60.45 x 89.92 cm" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Mid-Century Curved Wood Table Home Office Computer Desk, 48.4"L, Walnut" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Industrial Metal Office Computer Desk, 60"W, Power Sit to Standing Table, Brown/Black" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian Indre 1-Drawer Desk, 56 x 110 x 73cm, Light Brown/Oak Foil Finish" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Mid-Century Desk - 35 Inch, Natural" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian Côa 4-Drawer Desk, 160 x 73 x 77.5cm, Vintage Dark Brown Oak-Effect/Black Metal" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Avery Industrial Home Office Writing Desk with Metal Base, 40"W, Chestnut Brown Finish" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "AmazonBasics 40" Multipurpose Foldable Computer Study Desk - Natural" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "AmazonBasics Sedia direzionale da ufficio con schienale alto, regolabile in altezza - Marrone" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Ashworth Armless Velvet Accent Chair, 21.6"W, Navy" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Ravenna Home Armless Tufted Turned Wood Leg Accent Chair, 29"W, Blue" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Ravenna Home Tufted Armless English Roll Traditional Accent Chair, 26.8"W, Merlot Red" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Phoenix Home PU Leather Dining Chair Set of 2, 18.11" Length x 21.65" Width x 30.7" Height, Brown" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian Square" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Ravenna Home Dining Chairs, Set of 2, 40"H, Praline" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Modern Farmhouse Birch Dining Chair, 17.5"W, Dark Gray" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Mid-Century Beech and Rattan Dining Chair with Arms, 21.9"W, Natural" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Char 2" by DimaSP (https://sketchfab.com/3d-models/47a690dcecf847fca99c4f89111db85b), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "chare" by DimaSP (https://sketchfab.com/3d-models/acf6497a3d274d90ad3750510348f07a), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Chair" by 杭州维界科技有限公司 (https://sketchfab.com/3d-models/d2785b57e7da45858f2fe8bf4dedd68d), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Vida Designs Corona Wardrobe, 3 Door, Solid Pine Wood, Solid Pine Wood, Distressed Waxed Pine Bedroom Wooden Storage Mexican Furniture" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian Inari Modern 2-Door 2-Drawer Wardrobe, 100 x 57 x 180 cm, Light Brown Oak-Effect" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian Kolva Sliding 2-Door Wardrobe, 180 x 61 x 197cm, Light Brown Oak-Effect" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian Mira 4-Door Wardrobe with Mirrors, 181 x 207 x 58cm, Light Brown Oak-Effect" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Dikkies Closet" by klaxoneer (https://sketchfab.com/3d-models/05a035c3347645b8a7ceb6d65f825ac3), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Traditional Mennonite corner cabinet" by vinigor (https://sketchfab.com/3d-models/094697a23146463cb5564ac8bf89e5c4), CC BY-NC 4.0 (https://creativecommons.org/licenses/by-nc/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (licence flag: non_commercial)
- "Warn Wardrobe" by seenoise (https://sketchfab.com/3d-models/b3a99e956be64ab6958f7f5e1895f031), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Refrigerator - Grey Polished Metal" by Glowbox 3D (https://sketchfab.com/3d-models/2071bda681b642218b6829b82e4fd93b), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Old Fridge" by golddog (https://sketchfab.com/3d-models/68d69bbf7a454a09a2536ac0762532f3), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Haier Refrigerator" by cgwings (https://sketchfab.com/3d-models/c9c4e705bf794cb88d5d8726095f4917), CC BY-NC 4.0 (https://creativecommons.org/licenses/by-nc/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (licence flag: non_commercial)
- "Stove" by Daniyal Malik (https://sketchfab.com/3d-models/7c5c9dec5c2e4ff998c386410b0e3686), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Bathroom" by Thunder (https://sketchfab.com/3d-models/3eafb89804b54c8e8cbe35e4d456e0a9), CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched (licence flag: share_alike)
- "Ingstav147 PULT ZRK V1" by KRONZI (https://sketchfab.com/3d-models/8580c4545d1649efb3503c6c2a012641), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Sink" by Shining Salt (https://sketchfab.com/3d-models/ce1a06f7cbe1425099a145f851fc5dee), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Toilettes" by Lightningx (https://sketchfab.com/3d-models/0b3325fad3e740b1ac86173c90b56afd), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Toilet" by Xill (https://sketchfab.com/3d-models/24d1b493899d407780140688abae19bc), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Toilet" by Ali107_YT (https://sketchfab.com/3d-models/3446229dce1f47528fa871cc7669136c), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Home Corona 2 unità da 1 TV a schermo Piatto, supporto/ripostigli" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet King Street Industrial Cabinet Media Console Table With Functional Storage, Walnut, Black Metal, Glass" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Ferndale Rustic Reclaimed Pine Media TV Console Stand, 71"W, Sandstone" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Traditional Oak Wood Media TV Console Table, 59", Walnut Finish" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Bowlyn Mid-Century Modern Wood TV Media Table Stand, 64", Walnut" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "ROCKPOINT TV Stand, 42x16x23.6inch, Walnut Brown" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Roxmere Mid-Century Modern TV Media Console Center Stand, 59"W, Acacia Wood &amp; Dark Metal" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Movian TV Board for TVs up to 80 Inches" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian 2-Door 1-Shelf TV Stand, 176 x 40 x 58 cm, White and Oak Effect" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Larson Industrial Wood and Metal 4-Shelf Bookcase, 73"H, Walnut" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Casual Wood Bookcase, 34"W, Natural Rattan" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian Moselle 2-Door Cabinet/Bookcase with 8 Shelves, 139 x 100 x 45cm, Light Brown Oak-Effect/White" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Stone & Beam Rylee Modern Bookcase 39.4"Wx76.8”H, Mixed Gray" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Alkove Velle Bookcase, 42 x 95 x 202cm, Oiled Honey Oak" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Davenport Contemporary Shelf, 34"W, Elm and Metal" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Bookcase" by Bec (https://sketchfab.com/3d-models/4939d1bca386405f9cc22c48441b63de), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Scaffale B" by Francesco Coldesina (https://sketchfab.com/3d-models/68baafb344b2445a8e7f4917b6fe8a63), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Dusty Old Bookshelf (FREE)" by Brandon Westlake (https://sketchfab.com/3d-models/6c5ac2547db34c3c81b2e4808b000386), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Bookcase" by Icanreed (https://sketchfab.com/3d-models/b43c45317fd74a4aa9ba443b9a355ea3), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Solo 100シェルフ WN" by classe-saga (https://sketchfab.com/3d-models/eb98251fbccf4cdd8a3737362e2378e9), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Hallowood Waverly 1 Drawer Small Side Table in Light Oak Finish | Solid Wooden End/Lamp Stand/Bedside Cabinet/Nightstand, (WAV-LAM590)" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Newport Nightstand End Table, 22"W, Toffee Oak" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Alkove Hayes 1-Drawer Solid Wood Nightstand, 56 x 44 x 47cm, Wild Oak" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian Kyyvesi, 2-Drawer Storage Night Stand, 60 x 42 x 50 cm, Walnut Effect" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Rivet Mango Wood and Iron 3-Drawer Shutter Nightstand, 18"W, Natural Finish" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Vida Designs Corona Merchant Chest Of Drawers, 9 Drawer, Solid Pine Wood" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand - Movian Corona Sideboard, 1 Door 4 Drawer, Solid Pine Wood, 76 x 86 x 40 cm" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Vida Designs Corona Chest Of Drawers, 4 Drawer, Rustic, Solid Pine Wood." by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Glenwood Industrial Metal Dresser, 60"W, Oak" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet West, Mid-Century, Oak Distinct Grain, 6-Drawer Dresser, 60"W, Dark Oak Finish" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Parson 6-Drawer Wood Bedroom Dresser, 60"W, Natural" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Eastport Industrial Wood Dresser, 30"W, Oak Finish" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Gould Contemporary Wood Bedroom Dresser Chest, 18", Washed Navy and Gold" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Artum Hill BE6-802 Laurel Dresser, 5-Drawer, Modern Gray" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Modern Chest of Drawers with Diamond Pattern, 17.7 Inch Width, Natural" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Mid-Century Modern Round Black Wood Nesting Side End Table, 15.7" W, Dark Oak" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Larson Industrial Wood & Metal Side End Table, 27"W, Walnut" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Ferndale Rustic Reclaimed Pine Side End Table, 24"W, Sandstone" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Modern Rustic Reclaimed Elm Round Accent Side End Table, 16.9"W, Natural" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Stone & Beam Larson Industrial Wood & Metal Side End Table, 22"W, Set of 2, Walnut" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Ravenna Home Aubree Mid-Century Modern Shelf Storage Side Table, 23.6"W, Grey pine" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Ball & Cast End Table" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam 2-Tier Rustic Accent End Table, 26"W, Light Wood and Dark Metal" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Ravenna Home Damask-Pattern Ceramic Garden Stool or Side Table, 16"H, Grey" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Ravenna Home Clover-Pattern Ceramic Garden Stool or Side Table, 16"H, Grey" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Ravenna Home Moroccan-Pattern Ceramic Garden Stool or Side Table, 16"H, Grey" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Industrial Mango-Topped Side Table, 19.61"W" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Caden Adjustable Task Floor Lamp with Bulb, 60"H, Black and Brass" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Glass Column Brass Floor Lamp, With Bulb, Linen Shade, 13.0" x 13.0" x 59.0", Brushed Brass" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Rivet Mid-Century Modern Theory 5-Arm Living Room Floor Lamp with Edison Light Bulbs, 60"H, Black and Brass Finish" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Rivet Olive 4 Wood Shelf Standing Floor Lamp With Light Bulb and USB Charging Station - 11.8 x 11.8 x 62 Inches, Brass" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Mid-Century Modern Floor Lamp with Wireless USB Port Charging Wood Table, 59"H, Light Bulb Included, Black" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Ravenna Home Traditional Standing Floor Lamp with Reading Light and LED Light Bulb - 69.75 Inches, Brushed Nickel with Frosted Glass" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Ravenna Home Frosted Glass Living Room Standing Floor Lamp with LED Light Bulb - 69.75 Inches, Brushed Nickel" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Mid-Century Modern Henley Living Room Standing Floor Lamp with LED Light Bulb - 15 x 15 x 58 Inches, Matte Black and Antique Brass" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Ravenna Home Traditional Metal Floor Lamp with Stacked Oval Accents, LED Bulb Included, 58.5"H, Polished Nickel" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "lamp" by anish_ (https://sketchfab.com/3d-models/0eba4ad785674d3586aafc82854100fa), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "low poly Lamp 3d model" by mohamedvfx (https://sketchfab.com/3d-models/53409613b45b42b98b979f12ab8faa12), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Street lights" by U-like (https://sketchfab.com/3d-models/71853da424aa4b208e14f6cf430339ae), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Empty Flower Pot" by dumerlot (https://sketchfab.com/3d-models/41e58efcf647494483f9860df99acf60), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "succulent" by Elif Smbl (https://sketchfab.com/3d-models/57972124483145b4a4bbf4fd4caca6e7), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Cacti pot" by Spacyy (https://sketchfab.com/3d-models/71b53eaee72e4a829a9256a7bcfb7dab), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Succulent" by mika.rr (https://sketchfab.com/3d-models/9dd44cda400c48a083ffd9480067f04f), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "FlowerPot" by ibrahmcingi (https://sketchfab.com/3d-models/b99c584dd11d4691b5d13303383371e5), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "CGT 116 Wk8 Plant" by mlin234 (https://sketchfab.com/3d-models/bf122cd0854e422bb94704552c64810b), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Velvet Texture Decorative Throw Pillow, 17" x 17", Midnight" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Mojave-Inspired Decorative Throw Pillow Cover, 20" x 20", Black and Red" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Transitional Woven Diamond Decorative Throw Pillow, 20" x 20", Indigo" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Transitional Woven Diamond Decorative Throw Pillow Cover, 20" x 20", Indigo" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Modern Geometric Decorative Print Pillow Cover, 20" x 20", Black" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Shaggy Short Rug, 7'7" x 9'7", Ivory" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Mid-Century Modern Dusk Wool Rug, 5' x 8', Tan" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Diamond Trellis Tassel Wool Rug, 7'6" x 9'6", Ivory" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Swirling Paisley Farmhouse Motif Wool Runner Rug, 2' 6" x 8', Multi" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Contemporary Striated Jute Area Rug, 10' 6" x 8', Oatmeal" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Contemporary Striated Jute Area Rug, 5' 9" x 3' 9", Silver Birch" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Contemporary Striated Jute Area Rug, 10' 6" x 8', Off White" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Contemporary Striated Jute Rug, 10' 6" x 8', Citron" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Stone & Beam Rug, 3'11" x 5'11", Blue, Navy, Multicolor" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Stone & Beam Polypropylene Round Rug, 5'3" x 5'3", Gray, Orange, Multicolor" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Basics - 4'X6' Plush Diamond Trellis Shag Rug, Grey" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Modern Red and Gold Tulip Print on Canvas, Brown Frame, 13.75" x 13.75"" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet World Map Hemisphere Print in Black and White Vintage Wall Art, Black Frame, 30.5" x 30.5"" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Black and White Vintage Bike Print in White Frame, 15" x 21"" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Abstract Topographic Print in Black Wood Frame, 20" x 20"" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Modern White Framed Black and White Paris Map Print, 30" x 30"" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Modern Turquoise and Orange Palm Print in Gray Frame Wall Art, 12" x 12"" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Rivet Vintage Blue Yellow and Green Chairs in Gold Wood Frame Wall Art, 20" x 20"" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Amazon Brand – Stone & Beam Traditional Landscape Print with Copper Leaf Wall Art Decor on Canvas - 35" x 35"" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html; changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched

## Refused after judging

| uid | Source | Type | Reason |
|---|---|---|---|
| 0102b2c1449f448687d62ea66ae2a26a | objaverse | chair | over the per-type limit of the catalogue: rank 33 of 38 accepted chair models (keep 12) |
| 01b79647e6e442989fda47ff20cabdc9 | objaverse | armchair | over the per-type limit of the catalogue: rank 34 of 36 accepted armchair models (keep 12) |
| 01c53767c1f84f55ad9f46eb89949cf9 | objaverse | floor_lamp | every style family it fits already has 3 models of its type: rank 26: floor_lamp already has 3 models of each of its styles (classic) |
| 039c6026571943d6ac45c6816bcc7ff1 | objaverse | chair | every style family it fits already has 3 models of its type: rank 8: chair already has 3 models of each of its styles (classic) |
| 03cba69a2c3140f7abc013d42d455fba | objaverse | sofa | over the per-type limit of the catalogue: rank 35 of 36 accepted sofa models (keep 12) |
| 03f16302c1a54c46b438dac78e9d7048 | objaverse | chair | over the per-type limit of the catalogue: rank 31 of 38 accepted chair models (keep 12) |
| 03febdfb56cf419d89fe2d4eaa0bdb5e | objaverse | table_coffee | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 04bef8e589524b8c9d7a3bb206b206a8 | objaverse | potted_plant | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 05a4c8fccea2443f8bc67e4b3152e056 | objaverse | wardrobe | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry +Y |
| 0648e61d41504518a79b027332e67540 | objaverse | toilet | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| 06a5cfec9b87416b8b01a2e1239e62a1 | objaverse | toilet | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 0723b35415b0462eb5c01140b6b70340 | objaverse | chair | every style family it fits already has 3 models of its type: rank 7: chair already has 3 models of each of its styles (classic) |
| 072d0468bb97447ab1ca7e3edea25f1f | objaverse | sofa | over the per-type limit of the catalogue: rank 29 of 36 accepted sofa models (keep 12) |
| 08a3baeb2e0847939d53027824de5a49 | objaverse | wardrobe | every style family it fits already has 3 models of its type: rank 14: wardrobe already has 3 models of each of its styles (scandinavian, modern minimal, minimal, modern) |
| 08d73e1168504bf2b8706cd838ad16ef | objaverse | bookshelf | every style family it fits already has 3 models of its type: rank 23: bookshelf already has 3 models of each of its styles (modern) |
| 08f7f65edfea417b8ed9ca748381e507 | objaverse | bed_double | every style family it fits already has 3 models of its type: rank 8: bed_double already has 3 models of each of its styles (scandinavian, japandi, modern minimal, minimal, modern) |
| 0972c48a7e4548bca80975a47a823bab | objaverse | bed_double | front not agreed (judges and geometry or the documented front): judges: view 3 (-X); geometry +Y |
| 09ee59423b4b428f94f01fc5beccd227 | objaverse | armchair | every style family it fits already has 3 models of its type: rank 21: armchair already has 3 models of each of its styles (classic) |
| 0a34dc814a3a44cfa76388e732c05376 | objaverse | floor_lamp | every style family it fits already has 3 models of its type: rank 27: floor_lamp already has 3 models of each of its styles (classic) |
| 0cb0a6704c8a4fbd967039998a9d76ac | objaverse | bed_double | every style family it fits already has 3 models of its type: rank 22: bed_double already has 3 models of each of its styles (scandinavian, modern) |
| 12f297af37e9444dae34a02e86c4d36b | objaverse | potted_plant | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 132a8ee2af3a40d39d270fbed3d3666c | objaverse | toilet | front not agreed (judges and geometry or the documented front): judges: qwen 1, glm 0 |
| 13407a0758804fc09ec4c7e51e9f9d0e | objaverse | chair | over the per-type limit of the catalogue: rank 35 of 38 accepted chair models (keep 12) |
| 138f793adde045a5a5247edf48f61eb1 | objaverse | sofa | every style family it fits already has 3 models of its type: rank 20: sofa already has 3 models of each of its styles (modern minimal, modern) |
| 14791efb33314b02ac5ac74b47c36d14 | objaverse | bookshelf | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry undecided (open_side: panel fractions {'-x': 1.0245, '+x': 1.0313, '-y': 0.1149, '+y': 0.2505} give 0 axes with one closed side) |
| 15a583ac9db84a529e7ea1d2bd7eadbe | objaverse | fridge | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| 1625701880c54b7d9f50e77455cef39b | objaverse | chair | over the per-type limit of the catalogue: rank 32 of 38 accepted chair models (keep 12) |
| 17c796aeb1b8455d8f594a72490e11b7 | objaverse | washbasin | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 1a41218e823c4cba801bd2b3d71c9dff | objaverse | wardrobe | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 1b256f6ce7924f59a756fe8f7ba69416 | objaverse | desk | every style family it fits already has 3 models of its type: rank 12: desk already has 3 models of each of its styles (scandinavian, japandi, modern minimal, minimal, modern) |
| 1d18955742df45e9875b28d382a33ef3 | objaverse | wardrobe | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry +Y |
| 1d41e84fd76241e7a8929a314052269c | objaverse | table_coffee | every style family it fits already has 3 models of its type: rank 28: table_coffee already has 3 models of each of its styles (scandinavian, japandi, modern minimal, minimal, modern) |
| 1f07c148a7bc4e7c88dc57de50dc36b3 | objaverse | toilet | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry undecided (back_taller: offsets -0.057 (x) and +0.092 (y) do not single out one axis) |
| 23fa151346304c8bb8c58f58a76e6407 | objaverse | desk | front not agreed (judges and geometry or the documented front): judges: qwen 1, glm 3 |
| 257f44c12fa948deacca9995dbb70e7b | objaverse | potted_plant | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| 26b5f6c3ceb640d78829c0293c3ffbf9 | objaverse | table_dining | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 2b14055dc8054ec79b4d0d7e8f00be1e | objaverse | floor_lamp | every style family it fits already has 3 models of its type: rank 25: floor_lamp already has 3 models of each of its styles (modern) |
| 2b7d5c96159c42589dd970d81e877668 | objaverse | toilet | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 2bd3fcc82c9f43cfb0c8cf26c7d0107c | objaverse | bed_double | every style family it fits already has 3 models of its type: rank 20: bed_double already has 3 models of each of its styles (modern minimal, modern) |
| 2c32127e0a354be9b588bbeb8f9ac644 | objaverse | chair | over the per-type limit of the catalogue: rank 36 of 38 accepted chair models (keep 12) |
| 2f1706233a3248cf9a74586fc2e7120c | objaverse | bathtub | front not agreed (judges and geometry or the documented front): judges: qwen 2, glm 0 |
| 2ffb917efef043dbb7fe98f44d2d9b2b | objaverse | stove | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| 300ece91863242649e728e2f8d2a6bfe | objaverse | desk | every style family it fits already has 3 models of its type: rank 26: desk already has 3 models of each of its styles (modern minimal, minimal, modern) |
| 305f2b09e0de48bb919116026aba8f44 | objaverse | potted_plant | not the furniture type (a judge): qwen False, glm True |
| 309ccba7b2cb40a6bfffb89f498fc54c | objaverse | wardrobe | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry undecided (detail_side: vertex counts {'-x': 96, '+x': 96, '-y': 50, '+y': 51} give no side with 1.3x more detail) |
| 317dac94ec404bdbaa6d41a85e04f51c | objaverse | floor_lamp | not the furniture type (a judge): qwen False, glm True |
| 319ec67c98e447eebda0039b143274c5 | objaverse | bookshelf | front not agreed (judges and geometry or the documented front): judges: qwen 1, glm 3 |
| 322ba3a159a845c7b7642467e23fcc2d | objaverse | bed_single | front not agreed (judges and geometry or the documented front): judges: qwen 1, glm 3 |
| 3301331424bb4dbc8f06e2d3717bb067 | objaverse | floor_lamp | not the furniture type (a judge): qwen False, glm False |
| 33eb258d9873435690254cfbb0ea46ec | objaverse | floor_lamp | every style family it fits already has 3 models of its type: rank 9: floor_lamp already has 3 models of each of its styles (modern) |
| 351d798f9cc3451099200c5235aee352 | objaverse | chair | over the per-type limit of the catalogue: rank 37 of 38 accepted chair models (keep 12) |
| 3597a7a470ac4f81b1b362eea66f4d6f | objaverse | wardrobe | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 36f12a0c9c9149aab3dbe7fb35189fee | objaverse | table_coffee | every style family it fits already has 3 models of its type: rank 20: table_coffee already has 3 models of each of its styles (modern minimal, minimal, modern) |
| 39541d5daa7a4fba9614ad9847c992d5 | objaverse | desk | front not agreed (judges and geometry or the documented front): judges: qwen 2, glm 0 |
| 3b1033c7d6c84db8b0850121363b65ef | objaverse | potted_plant | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| 3d118a9fd6e34ddab99cb0fab5540682 | objaverse | bed_single | front not agreed (judges and geometry or the documented front): judges: qwen 2, glm 0 |
| 3de2e575e8b941dd94ae08158636b20a | objaverse | table_dining | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 3ee00f7e14674461af4241f5ef7ed039 | objaverse | desk | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| 4112e07e262842c6b7070aa1505505c3 | objaverse | wardrobe | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry +Y |
| 426c14adba6a45638752986c2f7d16b2 | objaverse | bed_double | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 42da0122f2134a189767d0911b401c1c | objaverse | sofa | over the per-type limit of the catalogue: rank 32 of 36 accepted sofa models (keep 12) |
| 4825d2d251b648f583db7147a7fd8d63 | objaverse | potted_plant | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 482c5168f1694911b597c81f3d0c73b1 | objaverse | sofa | over the per-type limit of the catalogue: rank 36 of 36 accepted sofa models (keep 12) |
| 4a056ba4d1ec48e9b4d7f30646f71052 | objaverse | toilet | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| 4a0f306ba95144fda533b329818d0680 | objaverse | floor_lamp | not the furniture type (a judge): qwen False, glm False |
| 4ae706aa53c043fa8261ebf40f580303 | objaverse | potted_plant | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| 4fdd0158c80c4de2a1b1bd5e0c77543a | objaverse | desk | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 51b1fdccb6bb40a181df054fcf8d2e31 | objaverse | fridge | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| 51d928b33e5549898cc86cbdaf966d83 | objaverse | bookshelf | every style family it fits already has 3 models of its type: rank 22: bookshelf already has 3 models of each of its styles (modern minimal, minimal) |
| 536dbfc2fdbe4dec9203ab390b9a6eda | objaverse | bathtub | front not agreed (judges and geometry or the documented front): judges: qwen 2, glm 0 |
| 55325e3b09ac48b2ae3803bccf804741 | objaverse | fridge | front not agreed (judges and geometry or the documented front): judges: qwen 1, glm 3 |
| 568f22034e364caca4e450a6d534dbd6 | objaverse | bed_double | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| 580ba3b412a24ee29c62a9ccf6bdc80c | objaverse | stove | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 5847113c458f4a2483aedd663376c7de | objaverse | table_dining | every style family it fits already has 3 models of its type: rank 22: table_dining already has 3 models of each of its styles (minimal, modern) |
| 592d31f4896948bb9ac5e53ac246d8c8 | objaverse | stove | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| 592e740e6310420e957657c16d830102 | objaverse | desk | every style family it fits already has 3 models of its type: rank 23: desk already has 3 models of each of its styles (modern) |
| 5ab48fd4819745b596df3ea39908e2e7 | objaverse | table_coffee | every style family it fits already has 3 models of its type: rank 33: table_coffee already has 3 models of each of its styles (modern minimal, minimal) |
| 5b9e8ba19b1b454f82898ac4809f02b2 | objaverse | armchair | every style family it fits already has 3 models of its type: rank 12: armchair already has 3 models of each of its styles (classic) |
| 5dbfe3c5798445a5bdff4efca0b943a2 | objaverse | bed_single | front not agreed (judges and geometry or the documented front): judges: qwen 1, glm 3 |
| 5ec9697d85654005b27fd29bd6df987e | objaverse | sofa | front not agreed (judges and geometry or the documented front): judges: qwen 2, glm 0 |
| 5f235f066a9a416fb7177496a9117ec7 | objaverse | table_dining | every style family it fits already has 3 models of its type: rank 23: table_dining already has 3 models of each of its styles (modern minimal, modern) |
| 604886640ac948f1980d81bc4a3ed7cf | objaverse | bed_double | front not agreed (judges and geometry or the documented front): judges: qwen 1, glm 0 |
| 624c9f7dcb2f4acd93237591ef10c76a | objaverse | chair | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 63797942d2674b6da5c94ce19672e6b6 | objaverse | chair | every style family it fits already has 3 models of its type: rank 10: chair already has 3 models of each of its styles (classic) |
| 653a622f383244ab9e7859f9aa2dcc8f | objaverse | bed_single | front not agreed (judges and geometry or the documented front): judges: view 3 (-X); geometry -Y |
| 65a13a04056c4f51a9c324e2a975b9a5 | objaverse | bed_double | not the furniture type (a judge): qwen False, glm True |
| 65e5c193702e4be9beb5ec783c422b5e | objaverse | chair | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| 674b6c07743e4f569d4b745949d1a0f1 | objaverse | bathtub | front not agreed (judges and geometry or the documented front): judges: qwen 3, glm 2 |
| 68f2b9fd83b349f9b285c360c447edbf | objaverse | table_coffee | every style family it fits already has 3 models of its type: rank 31: table_coffee already has 3 models of each of its styles (japandi, modern minimal, modern) |
| 69f1c0489a144f3c98e66dcfe72b3969 | objaverse | armchair | every style family it fits already has 3 models of its type: rank 9: armchair already has 3 models of each of its styles (classic) |
| 6c6a1f5757b34f7485133a91bb85cabe | objaverse | bathtub | not a single object (a judge): qwen False, glm True |
| 6d443f619ecd404a81769c70f447ba86 | objaverse | wardrobe | every style family it fits already has 3 models of its type: rank 16: wardrobe already has 3 models of each of its styles (scandinavian, modern minimal, minimal, modern) |
| 6f79223d321047059e1032c78b1b00a5 | objaverse | table_coffee | every style family it fits already has 3 models of its type: rank 19: table_coffee already has 3 models of each of its styles (scandinavian, japandi, modern minimal, minimal, modern) |
| 6f7bb38a14544f65902b10ec921fe57e | objaverse | armchair | every style family it fits already has 3 models of its type: rank 23: armchair already has 3 models of each of its styles (classic) |
| 70b7b418af714050aa83e99deb2253b7 | objaverse | wardrobe | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry +Y |
| 71af93b1d15f4f48ad836d36110626f7 | objaverse | bookshelf | no style both judges name: qwen ['modern minimal', 'minimal', 'japandi', 'scandinavian'], glm ['modern', 'neutral'] |
| 724d93a7f3644f96909e8c55909c6418 | objaverse | table_dining | every style family it fits already has 3 models of its type: rank 24: table_dining already has 3 models of each of its styles (scandinavian, rustic) |
| 736e3ea67480426da4013dbca5fb8d20 | objaverse | sofa | over the per-type limit of the catalogue: rank 34 of 36 accepted sofa models (keep 12) |
| 757961eb75a64dc689f2047ae8cdbd3b | objaverse | wardrobe | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 75a7a3a8146849dea698cfd04f73482b | objaverse | fridge | every style family it fits already has 3 models of its type: rank 4: fridge already has 3 models of each of its styles (modern minimal, modern) |
| 75aa9519195647d99cf1e2d4863dbe87 | objaverse | bookshelf | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry undecided (open_side: panel fractions {'-x': 0.8648, '+x': 0.8528, '-y': 0.0033, '+y': 0.0} give 0 axes with one closed side) |
| 774971f63ea54cdba8119439f4ff09c5 | objaverse | table_dining | photoreal quality below 4 (a judge): qwen 3, glm 5 |
| 77c0313ad21144dcb904915d66a163b3 | objaverse | bookshelf | front not agreed (judges and geometry or the documented front): judges: qwen 2, glm 3 |
| 7a545709aa98429a9b30f812f70193f7 | objaverse | bookshelf | every style family it fits already has 3 models of its type: rank 13: bookshelf already has 3 models of each of its styles (modern minimal, minimal) |
| 7aa2f0637fde49fca76cd0651936dec4 | objaverse | desk | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| 7ad37a39f5534d57bfb68f34fe0fbd22 | objaverse | potted_plant | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 7b13b36ba2304912afc9840caea731c6 | objaverse | bed_single | front not agreed (judges and geometry or the documented front): judges: view 3 (-X); geometry undecided (back_taller: top centroid offset -0.006 of the extent on x is below 0.08: no taller side) |
| 7d5367e51dca4a50a101b1089149ccde | objaverse | wardrobe | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry +Y |
| 7e7cc43a2fb84e44a03a67fecdd76ba8 | objaverse | desk | front not agreed (judges and geometry or the documented front): judges: view 1 (+X); geometry undecided (detail_side: only 2 vertices at the x sides) |
| 7ea7b60be1a0412b87d330148229b932 | objaverse | toilet | every style family it fits already has 3 models of its type: rank 4: toilet already has 3 models of each of its styles (modern minimal, minimal, modern) |
| 7f92080d86484d81b8dd30317bb28586 | objaverse | desk | every style family it fits already has 3 models of its type: rank 25: desk already has 3 models of each of its styles (modern minimal, minimal, modern) |
| 800d3c5569b94abfa2da7976504d589d | objaverse | bathtub | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry +Y |
| 804fa46335874949938b6dfb55d17820 | objaverse | bathtub | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry +Y |
| 8096984ae8734db9bfa5dedf89c175a7 | objaverse | sofa | over the per-type limit of the catalogue: rank 28 of 36 accepted sofa models (keep 12) |
| 813f5aeef3f3430d947f3879c6941719 | objaverse | floor_lamp | no style both judges name: qwen ['classic'], glm ['neutral'] |
| 815bd9cee3644f3f8996b4a6d123c7c3 | objaverse | desk | front not agreed (judges and geometry or the documented front): judges: qwen 2, glm 0 |
| 8170cf1409924abc9c3fc8becccdd36e | objaverse | floor_lamp | every style family it fits already has 3 models of its type: rank 28: floor_lamp already has 3 models of each of its styles (modern) |
| 81ada0e24e1647d8a0d6d0708a696f84 | objaverse | bed_single | front not agreed (judges and geometry or the documented front): judges: qwen 2, glm 0 |
| 821c4d9f12294380a9b0757b4adbb379 | objaverse | table_coffee | every style family it fits already has 3 models of its type: rank 21: table_coffee already has 3 models of each of its styles (japandi, modern minimal, minimal, modern) |
| 87eab647ca624962a7c178c0105643aa | objaverse | bookshelf | every style family it fits already has 3 models of its type: rank 24: bookshelf already has 3 models of each of its styles (modern minimal, minimal, modern) |
| 887092793d0b402e8571eda2d1a47cb4 | objaverse | potted_plant | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| 8a22e1fd8600472597bfe478e7d0c9ba | objaverse | armchair | front not agreed (judges and geometry or the documented front): judges: view 1 (+X); geometry undecided (back_taller: offsets -0.181 (x) and -0.142 (y) do not single out one axis) |
| 8b099a2dfafc4436890eeaa7e928fd9b | objaverse | floor_lamp | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| 8cd4ef86c0914b95a181473230c77eda | objaverse | stove | front not agreed (judges and geometry or the documented front): judges: qwen 1, glm 0 |
| 8e1fddb38fa8400c9fcc784abe29aaaa | objaverse | fridge | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry +Y |
| 8ebdabed48ed4963887435aa05f0b874 | objaverse | armchair | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 8fba1e7048c0421fb7e6b6e8be8fce88 | objaverse | stove | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 90a0093f27f04ea19e33591f22910741 | objaverse | wardrobe | no style both judges name: qwen ['classic'], glm ['scandinavian', 'rustic', 'neutral'] |
| 90e9ccdd97f74104b5310772a984ca49 | objaverse | fridge | every style family it fits already has 3 models of its type: rank 5: fridge already has 3 models of each of its styles (modern minimal, modern) |
| 9155b2b4be5f452a98837459112a3b9b | objaverse | potted_plant | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 9234d8196b73434684bcbb8092cc9e2a | objaverse | chair | over the per-type limit of the catalogue: rank 29 of 38 accepted chair models (keep 12) |
| 93ce115ac08d4365bc9a8d9e386bd166 | objaverse | desk | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry undecided (detail_side: vertex counts {'-x': 326, '+x': 314, '-y': 84, '+y': 84} give no side with 1.3x more detail) |
| 955cf512b86c4a799aa3ef391d670e55 | objaverse | wardrobe | front not agreed (judges and geometry or the documented front): judges: view 3 (-X); geometry undecided (detail_side: x ratio 1.47 and y ratio 1.43 do not single out one axis) |
| 956a47ccc1a54a40a8711f3852d54433 | objaverse | table_coffee | every style family it fits already has 3 models of its type: rank 9: table_coffee already has 3 models of each of its styles (modern minimal, modern) |
| 961af2daa6344e4fba0c7a4c92ff91f8 | objaverse | bookshelf | front not agreed (judges and geometry or the documented front): judges: view 3 (-X); geometry undecided (open_side: panel fractions {'-x': 0.0, '+x': 0.0, '-y': 0.8192, '+y': 0.8192} give 0 axes with one closed side) |
| 978be96600a0434e853c938e93b9c893 | objaverse | armchair | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 98b39c575de547a483f8fbaec2c0242f | objaverse | potted_plant | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| 9a2c5ed79d634a61b1166836a8a5530f | objaverse | sofa | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 9b1e09abe5e34d6397937ebf59901898 | objaverse | sofa | over the per-type limit of the catalogue: rank 30 of 36 accepted sofa models (keep 12) |
| 9c242421a7c1447f941f72b57e7473e5 | objaverse | sofa | over the per-type limit of the catalogue: rank 31 of 36 accepted sofa models (keep 12) |
| 9c4935439367490b8039a3cad9c46243 | objaverse | sofa | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| 9db7f69324c748e6bfbed697c5afaa1e | objaverse | toilet | front not agreed (judges and geometry or the documented front): judges: view 3 (-X); geometry -Y |
| a07501cd7f6c40fc9cf4cf438e41bac1 | objaverse | armchair | every style family it fits already has 3 models of its type: rank 11: armchair already has 3 models of each of its styles (classic) |
| a0d66f10a850469c9cb04c3cecc62a05 | objaverse | sofa | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| a4d6a4618f554e5986fd94e04720488c | objaverse | armchair | over the per-type limit of the catalogue: rank 35 of 36 accepted armchair models (keep 12) |
| a51e4acfdbb349c7876d7c37d2a0ee87 | objaverse | chair | every style family it fits already has 3 models of its type: rank 23: chair already has 3 models of each of its styles (minimal, modern) |
| a5eea808dc20404cb5f9e05680f7362f | objaverse | wardrobe | not the furniture type (a judge): qwen False, glm True |
| a755d424dd1d4a69a854ac02f7f86f83 | objaverse | armchair | front not agreed (judges and geometry or the documented front): judges: view 3 (-X); geometry undecided (back_taller: offsets +0.167 (x) and +0.126 (y) do not single out one axis) |
| a82bff9b83be4072871d3e2afc6cec14 | objaverse | fridge | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry +X |
| a8d11ec939064c009b726de5dcedbda2 | objaverse | potted_plant | not the furniture type (a judge): qwen False, glm True |
| a9917037f0c643dbbde0475b59bc53b1 | objaverse | table_coffee | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| aa9a7f23471a4bb6b461d5240c2bf1a7 | objaverse | bookshelf | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry undecided (open_side: panel fractions {'-x': 0.2845, '+x': 0.2274, '-y': 0.0427, '+y': 0.1454} give 0 axes with one closed side) |
| abbf0e6901484c05a68d2c6c485bdd9e | objaverse | table_coffee | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B00NUS53CY | abo | bookshelf | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B00NUS5GXA | abo | bookshelf | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B0154VUESC | abo | bed_double | every style family it fits already has 3 models of its type: rank 13: bed_double already has 3 models of each of its styles (modern minimal, minimal, modern) |
| abo_B01557QQSW | abo | dresser | every style family it fits already has 3 models of its type: rank 10: dresser already has 3 models of each of its styles (scandinavian, modern minimal, minimal, modern) |
| abo_B015IPNVFW | abo | wardrobe | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B01DA8QJYO | abo | tv_unit | every style family it fits already has 3 models of its type: rank 7: tv_unit already has 3 models of each of its styles (japandi) |
| abo_B01LWVEZ1C | abo | table_coffee | every style family it fits already has 3 models of its type: rank 14: table_coffee already has 3 models of each of its styles (scandinavian, japandi, modern minimal, minimal, modern) |
| abo_B01LYBQXRH | abo | bookshelf | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| abo_B01M0ZVGCQ | abo | bed_double | every style family it fits already has 3 models of its type: rank 11: bed_double already has 3 models of each of its styles (modern minimal, minimal) |
| abo_B01M4OYBOI | abo | table_coffee | every style family it fits already has 3 models of its type: rank 24: table_coffee already has 3 models of each of its styles (scandinavian, japandi, modern minimal, minimal, modern) |
| abo_B01M642Q91 | abo | table_coffee | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B01MXKMRK4 | abo | desk | every style family it fits already has 3 models of its type: rank 11: desk already has 3 models of each of its styles (modern minimal, industrial) |
| abo_B01N3MBCKT | abo | side_table | every style family it fits already has 3 models of its type: rank 16: side_table already has 3 models of each of its styles (scandinavian, japandi, modern minimal, minimal, modern) |
| abo_B01N6AQX0A | abo | bed_double | every style family it fits already has 3 models of its type: rank 9: bed_double already has 3 models of each of its styles (modern minimal, minimal, modern) |
| abo_B01NCOR0VZ | abo | table_coffee | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| abo_B07124WCZY | abo | armchair | no style both judges name: qwen ['modern', 'scandinavian', 'japandi', 'minimal'], glm ['classic', 'neutral'] |
| abo_B0714MMHBL | abo | rug | every style family it fits already has 3 models of its type: rank 8: rug already has 3 models of each of its styles (neutral) |
| abo_B0719STLSH | abo | rug | every style family it fits already has 3 models of its type: rank 9: rug already has 3 models of each of its styles (neutral) |
| abo_B071DZHLXH | abo | bookshelf | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| abo_B071FJR3SR | abo | dresser | every style family it fits already has 3 models of its type: rank 4: dresser already has 3 models of each of its styles (modern minimal) |
| abo_B071FJZVPH | abo | rug | every style family it fits already has 3 models of its type: rank 12: rug already has 3 models of each of its styles (neutral) |
| abo_B071FMSSWB | abo | sofa | every style family it fits already has 3 models of its type: rank 22: sofa already has 3 models of each of its styles (modern minimal, minimal, modern) |
| abo_B071FMSYCH | abo | armchair | over the per-type limit of the catalogue: rank 27 of 36 accepted armchair models (keep 12) |
| abo_B071H75K71 | abo | bed_single | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| abo_B071J7Q9X4 | abo | armchair | every style family it fits already has 3 models of its type: rank 20: armchair already has 3 models of each of its styles (modern) |
| abo_B071SHBTM5 | abo | dresser | every style family it fits already has 3 models of its type: rank 8: dresser already has 3 models of each of its styles (modern minimal, minimal) |
| abo_B071W2XLSC | abo | rug | every style family it fits already has 3 models of its type: rank 10: rug already has 3 models of each of its styles (classic) |
| abo_B07263589M | abo | sofa | every style family it fits already has 3 models of its type: rank 4: sofa already has 3 models of each of its styles (classic) |
| abo_B072M1WJ8S | abo | sofa | every style family it fits already has 3 models of its type: rank 19: sofa already has 3 models of each of its styles (modern minimal, modern) |
| abo_B072PWGSZL | abo | bed_double | every style family it fits already has 3 models of its type: rank 19: bed_double already has 3 models of each of its styles (modern minimal, modern) |
| abo_B072ZK2FZ6 | abo | table_coffee | every style family it fits already has 3 models of its type: rank 4: table_coffee already has 3 models of each of its styles (japandi, modern minimal, minimal, modern) |
| abo_B072ZK885L | abo | nightstand | front not agreed (judges and geometry or the documented front): judges: view 1 (+X); documented front -Y (ABO convention (3dmodels/README.md): glTF +Z points to the product's natural front = -Y in the importer's Z-up frame) |
| abo_B072ZMHBKQ | abo | nightstand | every style family it fits already has 3 models of its type: rank 11: nightstand already has 3 models of each of its styles (scandinavian, modern minimal, minimal, modern) |
| abo_B072ZMT5SD | abo | tv_unit | every style family it fits already has 3 models of its type: rank 15: tv_unit already has 3 models of each of its styles (modern minimal, minimal) |
| abo_B072ZNPRTC | abo | tv_unit | every style family it fits already has 3 models of its type: rank 12: tv_unit already has 3 models of each of its styles (scandinavian, japandi, modern minimal, minimal, modern) |
| abo_B0735CKFJK | abo | bookshelf | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B0735SLC3P | abo | rug | every style family it fits already has 3 models of its type: rank 21: rug already has 3 models of each of its styles (modern minimal, minimal, neutral) |
| abo_B07374C6R9 | abo | floor_lamp | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| abo_B073NZGLR7 | abo | wall_art | front not agreed (judges and geometry or the documented front): judges: view 2 (+Y); documented front -Y (ABO convention (3dmodels/README.md): glTF +Z points to the product's natural front = -Y in the importer's Z-up frame) |
| abo_B073NZT572 | abo | wall_art | every style family it fits already has 3 models of its type: rank 15: wall_art already has 3 models of each of its styles (modern minimal, minimal) |
| abo_B073NZT573 | abo | wall_art | photoreal quality below 4 (a judge): qwen 5, glm 3 |
| abo_B073NZT5CF | abo | wall_art | no style both judges name: qwen ['modern minimal', 'minimal', 'japandi', 'scandinavian'], glm ['neutral'] |
| abo_B073P13J4L | abo | wall_art | every style family it fits already has 3 models of its type: rank 14: wall_art already has 3 models of each of its styles (modern minimal, minimal, modern) |
| abo_B073P13J54 | abo | wall_art | every style family it fits already has 3 models of its type: rank 11: wall_art already has 3 models of each of its styles (scandinavian, modern minimal, minimal, modern) |
| abo_B073P14C3L | abo | wall_art | no style both judges name: qwen ['modern minimal', 'minimal', 'modern', 'japandi', 'scandinavian', 'neutral'], glm ['classic'] |
| abo_B073P15SD2 | abo | wall_art | every style family it fits already has 3 models of its type: rank 9: wall_art already has 3 models of each of its styles (modern minimal, minimal, modern) |
| abo_B073P19S7P | abo | wall_art | every style family it fits already has 3 models of its type: rank 12: wall_art already has 3 models of each of its styles (scandinavian, modern minimal, minimal, modern) |
| abo_B073P19TKF | abo | wall_art | front not agreed (judges and geometry or the documented front): judges: view 2 (+Y); documented front -Y (ABO convention (3dmodels/README.md): glTF +Z points to the product's natural front = -Y in the importer's Z-up frame) |
| abo_B073P1BKT1 | abo | wall_art | every style family it fits already has 3 models of its type: rank 10: wall_art already has 3 models of each of its styles (modern minimal, minimal, modern) |
| abo_B073P1N3GJ | abo | wall_art | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| abo_B073P3HHFT | abo | floor_lamp | every style family it fits already has 3 models of its type: rank 17: floor_lamp already has 3 models of each of its styles (industrial) |
| abo_B073P52NDX | abo | wall_art | every style family it fits already has 3 models of its type: rank 7: wall_art already has 3 models of each of its styles (modern minimal, minimal) |
| abo_B073P54PYL | abo | wall_art | every style family it fits already has 3 models of its type: rank 16: wall_art already has 3 models of each of its styles (modern minimal, minimal, modern) |
| abo_B073WQ8JLT | abo | bed_single | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B073WR5DGC | abo | bed_double | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| abo_B073WRLNS9 | abo | bed_double | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| abo_B0742D9X4R | abo | floor_lamp | every style family it fits already has 3 models of its type: rank 16: floor_lamp already has 3 models of each of its styles (modern minimal, minimal, modern) |
| abo_B0742DJS8J | abo | floor_lamp | every style family it fits already has 3 models of its type: rank 20: floor_lamp already has 3 models of each of its styles (modern minimal, modern) |
| abo_B074KKMQBG | abo | nightstand | every style family it fits already has 3 models of its type: rank 8: nightstand already has 3 models of each of its styles (modern minimal) |
| abo_B074KKXLK1 | abo | bookshelf | every style family it fits already has 3 models of its type: rank 5: bookshelf already has 3 models of each of its styles (modern minimal, minimal) |
| abo_B074KLRCPW | abo | table_coffee | every style family it fits already has 3 models of its type: rank 11: table_coffee already has 3 models of each of its styles (modern minimal, minimal, modern) |
| abo_B074VLRP9S | abo | cushion | every style family it fits already has 3 models of its type: rank 19: cushion already has 3 models of each of its styles (modern minimal, minimal) |
| abo_B075HR7KVR | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm False |
| abo_B075HR7LFF | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm False |
| abo_B075HR7LHQ | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm False |
| abo_B075HWDSC6 | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm False |
| abo_B075HWJ4K7 | abo | wall_art | every style family it fits already has 3 models of its type: rank 13: wall_art already has 3 models of each of its styles (modern minimal, minimal, modern) |
| abo_B075HWX45W | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm False |
| abo_B075HXHKZ4 | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm False |
| abo_B075HXMH4H | abo | wall_art | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| abo_B075NR8HWJ | abo | armchair | over the per-type limit of the catalogue: rank 26 of 36 accepted armchair models (keep 12) |
| abo_B075QDGZX7 | abo | bed_double | no style both judges name: qwen ['classic'], glm ['modern', 'neutral'] |
| abo_B075X2WN36 | abo | armchair | every style family it fits already has 3 models of its type: rank 7: armchair already has 3 models of each of its styles (modern) |
| abo_B075X2WNRP | abo | sofa | every style family it fits already has 3 models of its type: rank 10: sofa already has 3 models of each of its styles (modern) |
| abo_B075X4HZV6 | abo | armchair | no style both judges name: qwen ['classic'], glm ['neutral'] |
| abo_B075YMXWZC | abo | table_dining | every style family it fits already has 3 models of its type: rank 10: table_dining already has 3 models of each of its styles (scandinavian, modern minimal, minimal, modern) |
| abo_B075YPTG8S | abo | table_dining | every style family it fits already has 3 models of its type: rank 12: table_dining already has 3 models of each of its styles (modern minimal, modern, industrial) |
| abo_B075Z1NM5W | abo | tv_unit | every style family it fits already has 3 models of its type: rank 19: tv_unit already has 3 models of each of its styles (scandinavian, japandi, modern minimal, minimal, modern) |
| abo_B075Z6YRWQ | abo | tv_unit | every style family it fits already has 3 models of its type: rank 23: tv_unit already has 3 models of each of its styles (japandi, modern minimal, minimal, modern) |
| abo_B075ZGY571 | abo | rug | no style both judges name: qwen ['modern', 'minimal', 'scandinavian', 'japandi', 'neutral'], glm ['classic', 'rustic'] |
| abo_B076NNYB3P | abo | table_dining | every style family it fits already has 3 models of its type: rank 18: table_dining already has 3 models of each of its styles (modern minimal, minimal, modern) |
| abo_B077NZFT6C | abo | dresser | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B078JG4N1G | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm True |
| abo_B078JGHZSZ | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm True |
| abo_B079TXCC1J | abo | nightstand | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| abo_B079TXJNJD | abo | cushion | every style family it fits already has 3 models of its type: rank 9: cushion already has 3 models of each of its styles (modern, neutral) |
| abo_B079TYF1GK | abo | wardrobe | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B079V6V6TF | abo | cushion | every style family it fits already has 3 models of its type: rank 17: cushion already has 3 models of each of its styles (modern, neutral) |
| abo_B079V9CJB5 | abo | cushion | every style family it fits already has 3 models of its type: rank 12: cushion already has 3 models of each of its styles (scandinavian, neutral) |
| abo_B079VK52WZ | abo | nightstand | every style family it fits already has 3 models of its type: rank 14: nightstand already has 3 models of each of its styles (modern minimal, minimal, modern) |
| abo_B079VKDKC1 | abo | nightstand | every style family it fits already has 3 models of its type: rank 17: nightstand already has 3 models of each of its styles (modern minimal, minimal, modern) |
| abo_B079VNKB6Z | abo | nightstand | every style family it fits already has 3 models of its type: rank 7: nightstand already has 3 models of each of its styles (modern minimal, modern) |
| abo_B079VNL3CG | abo | nightstand | every style family it fits already has 3 models of its type: rank 18: nightstand already has 3 models of each of its styles (modern minimal, minimal) |
| abo_B079X4CP3F | abo | dresser | every style family it fits already has 3 models of its type: rank 11: dresser already has 3 models of each of its styles (modern minimal, minimal, modern) |
| abo_B079X4Z6QX | abo | dresser | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| abo_B07B4CZP32 | abo | armchair | every style family it fits already has 3 models of its type: rank 17: armchair already has 3 models of each of its styles (modern) |
| abo_B07B4DBBPG | abo | sofa | every style family it fits already has 3 models of its type: rank 23: sofa already has 3 models of each of its styles (modern minimal, modern) |
| abo_B07B4MSP7T | abo | armchair | every style family it fits already has 3 models of its type: rank 14: armchair already has 3 models of each of its styles (classic) |
| abo_B07B4SDNQT | abo | rug | every style family it fits already has 3 models of its type: rank 14: rug already has 3 models of each of its styles (neutral) |
| abo_B07B4SDVG3 | abo | rug | every style family it fits already has 3 models of its type: rank 13: rug already has 3 models of each of its styles (neutral) |
| abo_B07B4SDWVF | abo | rug | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| abo_B07B4SDZ7T | abo | rug | every style family it fits already has 3 models of its type: rank 22: rug already has 3 models of each of its styles (modern minimal, minimal, neutral) |
| abo_B07B4SF23K | abo | rug | every style family it fits already has 3 models of its type: rank 20: rug already has 3 models of each of its styles (neutral) |
| abo_B07B4WGGZR | abo | rug | every style family it fits already has 3 models of its type: rank 18: rug already has 3 models of each of its styles (scandinavian, japandi, modern minimal, minimal, modern, neutral) |
| abo_B07B4WKLZ7 | abo | rug | every style family it fits already has 3 models of its type: rank 19: rug already has 3 models of each of its styles (scandinavian, modern minimal, minimal, modern) |
| abo_B07B4YNHSN | abo | bed_double | every style family it fits already has 3 models of its type: rank 10: bed_double already has 3 models of each of its styles (modern minimal) |
| abo_B07B7DKRW4 | abo | desk | every style family it fits already has 3 models of its type: rank 20: desk already has 3 models of each of its styles (modern minimal, minimal, modern) |
| abo_B07B7GYMQ9 | abo | tv_unit | every style family it fits already has 3 models of its type: rank 21: tv_unit already has 3 models of each of its styles (modern minimal) |
| abo_B07B7GZTNR | abo | bookshelf | every style family it fits already has 3 models of its type: rank 20: bookshelf already has 3 models of each of its styles (modern minimal) |
| abo_B07B7J5BC2 | abo | tv_unit | every style family it fits already has 3 models of its type: rank 20: tv_unit already has 3 models of each of its styles (modern minimal) |
| abo_B07B7J5XSQ | abo | side_table | every style family it fits already has 3 models of its type: rank 9: side_table already has 3 models of each of its styles (modern minimal, modern) |
| abo_B07B7J8CGH | abo | side_table | every style family it fits already has 3 models of its type: rank 10: side_table already has 3 models of each of its styles (scandinavian, japandi, modern minimal, minimal, modern) |
| abo_B07B7J8FV9 | abo | side_table | every style family it fits already has 3 models of its type: rank 11: side_table already has 3 models of each of its styles (scandinavian, minimal, modern) |
| abo_B07B7J8HFV | abo | side_table | every style family it fits already has 3 models of its type: rank 15: side_table already has 3 models of each of its styles (modern minimal, minimal) |
| abo_B07B82PXCW | abo | table_dining | not the furniture type (a judge): qwen False, glm True |
| abo_B07B87J7L3 | abo | table_dining | not the furniture type (a judge): qwen False, glm True |
| abo_B07B8MTV4L | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm False |
| abo_B07B8P1JGF | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm False |
| abo_B07B8RYY41 | abo | tv_unit | every style family it fits already has 3 models of its type: rank 13: tv_unit already has 3 models of each of its styles (japandi, modern minimal, minimal, modern) |
| abo_B07BMQ64HR | abo | cushion | every style family it fits already has 3 models of its type: rank 6: cushion already has 3 models of each of its styles (neutral) |
| abo_B07BMQXWX1 | abo | cushion | every style family it fits already has 3 models of its type: rank 21: cushion already has 3 models of each of its styles (neutral) |
| abo_B07BMT4F21 | abo | cushion | every style family it fits already has 3 models of its type: rank 14: cushion already has 3 models of each of its styles (modern, neutral) |
| abo_B07BMTN6GF | abo | cushion | every style family it fits already has 3 models of its type: rank 5: cushion already has 3 models of each of its styles (neutral) |
| abo_B07BMTNH22 | abo | cushion | every style family it fits already has 3 models of its type: rank 13: cushion already has 3 models of each of its styles (modern, neutral) |
| abo_B07BMTXHSR | abo | cushion | every style family it fits already has 3 models of its type: rank 15: cushion already has 3 models of each of its styles (modern, neutral) |
| abo_B07BMTXJ1V | abo | cushion | every style family it fits already has 3 models of its type: rank 20: cushion already has 3 models of each of its styles (neutral) |
| abo_B07BMTXJ6B | abo | cushion | no style both judges name: qwen ['modern minimal', 'minimal', 'modern'], glm ['neutral'] |
| abo_B07BMTXRR1 | abo | cushion | every style family it fits already has 3 models of its type: rank 23: cushion already has 3 models of each of its styles (scandinavian, neutral) |
| abo_B07BWJCBY2 | abo | sofa | every style family it fits already has 3 models of its type: rank 6: sofa already has 3 models of each of its styles (classic) |
| abo_B07BWMSM1J | abo | armchair | every style family it fits already has 3 models of its type: rank 19: armchair already has 3 models of each of its styles (modern) |
| abo_B07C8MSZ5T | abo | cushion | every style family it fits already has 3 models of its type: rank 18: cushion already has 3 models of each of its styles (modern) |
| abo_B07C8MT64T | abo | cushion | every style family it fits already has 3 models of its type: rank 16: cushion already has 3 models of each of its styles (modern, neutral) |
| abo_B07C8WCWWK | abo | cushion | every style family it fits already has 3 models of its type: rank 8: cushion already has 3 models of each of its styles (modern, neutral) |
| abo_B07C9W437G | abo | chair | every style family it fits already has 3 models of its type: rank 12: chair already has 3 models of each of its styles (modern minimal, modern) |
| abo_B07C9YVDHJ | abo | tv_unit | every style family it fits already has 3 models of its type: rank 9: tv_unit already has 3 models of each of its styles (modern) |
| abo_B07D4F6ZKH | abo | chair | every style family it fits already has 3 models of its type: rank 22: chair already has 3 models of each of its styles (modern) |
| abo_B07DBB7831 | abo | nightstand | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| abo_B07DBB7FVP | abo | nightstand | no style both judges name: qwen ['modern minimal', 'minimal', 'modern'], glm ['classic', 'rustic'] |
| abo_B07DBCN3KB | abo | floor_lamp | no style both judges name: qwen ['classic'], glm ['modern', 'industrial'] |
| abo_B07DBDMN5F | abo | table_coffee | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| abo_B07DBDX1P2 | abo | armchair | over the per-type limit of the catalogue: rank 30 of 36 accepted armchair models (keep 12) |
| abo_B07DBF3VJY | abo | table_coffee | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B07DBFQV23 | abo | table_coffee | every style family it fits already has 3 models of its type: rank 5: table_coffee already has 3 models of each of its styles (modern minimal, modern) |
| abo_B07DBG898G | abo | sofa | every style family it fits already has 3 models of its type: rank 21: sofa already has 3 models of each of its styles (modern minimal, modern) |
| abo_B07DBHM1SZ | abo | floor_lamp | no style both judges name: qwen ['classic'], glm ['modern', 'industrial'] |
| abo_B07DMHP1ZY | abo | side_table | every style family it fits already has 3 models of its type: rank 19: side_table already has 3 models of each of its styles (minimal, modern) |
| abo_B07DMHTGJD | abo | bookshelf | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| abo_B07DVRLW48 | abo | nightstand | every style family it fits already has 3 models of its type: rank 12: nightstand already has 3 models of each of its styles (modern minimal, minimal) |
| abo_B07DVVKD85 | abo | nightstand | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| abo_B07DYV7WN2 | abo | chair | every style family it fits already has 3 models of its type: rank 18: chair already has 3 models of each of its styles (modern) |
| abo_B07F3XLTRH | abo | side_table | every style family it fits already has 3 models of its type: rank 18: side_table already has 3 models of each of its styles (modern minimal, minimal, modern) |
| abo_B07F49VHB8 | abo | table_coffee | every style family it fits already has 3 models of its type: rank 22: table_coffee already has 3 models of each of its styles (minimal, modern) |
| abo_B07FK1HLZ4 | abo | dresser | every style family it fits already has 3 models of its type: rank 17: dresser already has 3 models of each of its styles (scandinavian, japandi, modern minimal, minimal, modern, rustic) |
| abo_B07FK69CKR | abo | armchair | every style family it fits already has 3 models of its type: rank 15: armchair already has 3 models of each of its styles (modern) |
| abo_B07G527L5S | abo | table_coffee | every style family it fits already has 3 models of its type: rank 25: table_coffee already has 3 models of each of its styles (modern minimal, minimal, modern) |
| abo_B07GDYVV9M | abo | table_coffee | every style family it fits already has 3 models of its type: rank 7: table_coffee already has 3 models of each of its styles (scandinavian, japandi, modern minimal, minimal, modern) |
| abo_B07GF5DCK2 | abo | desk | every style family it fits already has 3 models of its type: rank 18: desk already has 3 models of each of its styles (scandinavian, modern minimal, modern) |
| abo_B07GFDZW5W | abo | bed_double | every style family it fits already has 3 models of its type: rank 6: bed_double already has 3 models of each of its styles (modern minimal, modern) |
| abo_B07GFFPKFV | abo | wardrobe | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B07GFFR415 | abo | bed_double | every style family it fits already has 3 models of its type: rank 14: bed_double already has 3 models of each of its styles (scandinavian, modern minimal, minimal) |
| abo_B07GFL6RF5 | abo | desk | every style family it fits already has 3 models of its type: rank 14: desk already has 3 models of each of its styles (scandinavian, modern minimal, minimal, modern) |
| abo_B07GFRCLMN | abo | desk | every style family it fits already has 3 models of its type: rank 21: desk already has 3 models of each of its styles (scandinavian, modern minimal, minimal, modern) |
| abo_B07GFS1R5B | abo | wardrobe | every style family it fits already has 3 models of its type: rank 9: wardrobe already has 3 models of each of its styles (modern minimal, minimal, modern) |
| abo_B07GFS1V51 | abo | desk | every style family it fits already has 3 models of its type: rank 17: desk already has 3 models of each of its styles (scandinavian, modern minimal, minimal, modern) |
| abo_B07GFS1WDY | abo | wardrobe | every style family it fits already has 3 models of its type: rank 4: wardrobe already has 3 models of each of its styles (modern minimal, minimal) |
| abo_B07GFSJ69T | abo | wardrobe | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B07GFWW3S8 | abo | wardrobe | every style family it fits already has 3 models of its type: rank 11: wardrobe already has 3 models of each of its styles (modern minimal, minimal) |
| abo_B07GFWW5JZ | abo | desk | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B07H8JN9QF | abo | wardrobe | every style family it fits already has 3 models of its type: rank 10: wardrobe already has 3 models of each of its styles (scandinavian, modern minimal, minimal, modern) |
| abo_B07H8PS4FZ | abo | wardrobe | every style family it fits already has 3 models of its type: rank 8: wardrobe already has 3 models of each of its styles (scandinavian, modern minimal, minimal, modern) |
| abo_B07H8SKPWP | abo | nightstand | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B07H8SQ2NZ | abo | bookshelf | every style family it fits already has 3 models of its type: rank 9: bookshelf already has 3 models of each of its styles (scandinavian, modern minimal, minimal, modern) |
| abo_B07H8SSJVW | abo | dresser | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B07H8SZNZF | abo | table_dining | every style family it fits already has 3 models of its type: rank 17: table_dining already has 3 models of each of its styles (scandinavian, modern minimal, minimal, modern) |
| abo_B07H8V7P3H | abo | wardrobe | every style family it fits already has 3 models of its type: rank 6: wardrobe already has 3 models of each of its styles (scandinavian, modern minimal, minimal, modern) |
| abo_B07HK3F2GG | abo | floor_lamp | every style family it fits already has 3 models of its type: rank 23: floor_lamp already has 3 models of each of its styles (modern minimal, minimal, modern) |
| abo_B07HK8NDXS | abo | floor_lamp | every style family it fits already has 3 models of its type: rank 19: floor_lamp already has 3 models of each of its styles (modern minimal, industrial) |
| abo_B07HSCJZQM | abo | bookshelf | every style family it fits already has 3 models of its type: rank 18: bookshelf already has 3 models of each of its styles (modern minimal, industrial) |
| abo_B07HSDP2CP | abo | dresser | every style family it fits already has 3 models of its type: rank 6: dresser already has 3 models of each of its styles (modern) |
| abo_B07HSKBHBT | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm False |
| abo_B07HSKY884 | abo | bookshelf | no style both judges name: qwen ['industrial'], glm ['modern minimal', 'minimal', 'modern'] |
| abo_B07HSLG6WN | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm False |
| abo_B07HZ1M12W | abo | sofa | every style family it fits already has 3 models of its type: rank 15: sofa already has 3 models of each of its styles (modern) |
| abo_B07HZ6SC9H | abo | sofa | every style family it fits already has 3 models of its type: rank 24: sofa already has 3 models of each of its styles (modern minimal, modern) |
| abo_B07HZ6VT4D | abo | sofa | every style family it fits already has 3 models of its type: rank 16: sofa already has 3 models of each of its styles (modern minimal, modern) |
| abo_B07HZ6X7ZK | abo | sofa | every style family it fits already has 3 models of its type: rank 18: sofa already has 3 models of each of its styles (modern) |
| abo_B07HZ72L2H | abo | sofa | every style family it fits already has 3 models of its type: rank 17: sofa already has 3 models of each of its styles (modern minimal, minimal, modern) |
| abo_B07J1YW3YT | abo | table_coffee | every style family it fits already has 3 models of its type: rank 26: table_coffee already has 3 models of each of its styles (scandinavian, japandi, modern minimal, minimal, modern) |
| abo_B07JGMW8DG | abo | wardrobe | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B07JGPKSBB | abo | tv_unit | every style family it fits already has 3 models of its type: rank 17: tv_unit already has 3 models of each of its styles (modern minimal, minimal, modern) |
| abo_B07JGY5LPJ | abo | wardrobe | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B07JKJSJB1 | abo | cushion | every style family it fits already has 3 models of its type: rank 11: cushion already has 3 models of each of its styles (scandinavian, neutral) |
| abo_B07JKJSTVJ | abo | cushion | every style family it fits already has 3 models of its type: rank 22: cushion already has 3 models of each of its styles (scandinavian, modern minimal, minimal, neutral) |
| abo_B07JM1H7RS | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm False |
| abo_B07JWP2Y5K | abo | dresser | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| abo_B07JXXR83F | abo | desk | every style family it fits already has 3 models of its type: rank 6: desk already has 3 models of each of its styles (scandinavian, modern minimal, modern) |
| abo_B07K6N3TNH | abo | desk | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B07K7K7GKC | abo | chair | every style family it fits already has 3 models of its type: rank 15: chair already has 3 models of each of its styles (scandinavian, japandi, modern minimal, minimal, modern) |
| abo_B07K7K8YF9 | abo | chair | over the per-type limit of the catalogue: rank 28 of 38 accepted chair models (keep 12) |
| abo_B07K7SJWCH | abo | table_dining | every style family it fits already has 3 models of its type: rank 19: table_dining already has 3 models of each of its styles (scandinavian, japandi, modern minimal, minimal, modern) |
| abo_B07K8V2SX3 | abo | armchair | over the per-type limit of the catalogue: rank 28 of 36 accepted armchair models (keep 12) |
| abo_B07L1DDXLR | abo | bed_double | every style family it fits already has 3 models of its type: rank 16: bed_double already has 3 models of each of its styles (modern minimal, modern) |
| abo_B07L1DH1PX | abo | nightstand | every style family it fits already has 3 models of its type: rank 10: nightstand already has 3 models of each of its styles (modern minimal, minimal) |
| abo_B07L85XV75 | abo | table_coffee | every style family it fits already has 3 models of its type: rank 6: table_coffee already has 3 models of each of its styles (scandinavian, japandi, modern minimal, minimal, modern) |
| abo_B07M6PHS9P | abo | chair | no style both judges name: qwen ['classic'], glm ['scandinavian', 'modern', 'neutral'] |
| abo_B07M6PJ4LX | abo | cushion | every style family it fits already has 3 models of its type: rank 7: cushion already has 3 models of each of its styles (scandinavian, neutral) |
| abo_B07M6PKC6B | abo | table_dining | every style family it fits already has 3 models of its type: rank 15: table_dining already has 3 models of each of its styles (scandinavian, minimal, modern) |
| abo_B07M6PKM8K | abo | chair | no style both judges name: qwen ['modern minimal', 'minimal', 'modern'], glm ['classic', 'neutral'] |
| abo_B07MBFCRD8 | abo | chair | no style both judges name: qwen ['classic'], glm ['scandinavian', 'modern', 'neutral'] |
| abo_B07MBFDL34 | abo | chair | over the per-type limit of the catalogue: rank 25 of 38 accepted chair models (keep 12) |
| abo_B07MBFDWNM | abo | floor_lamp | every style family it fits already has 3 models of its type: rank 18: floor_lamp already has 3 models of each of its styles (modern minimal, minimal, modern) |
| abo_B07MBFDWY5 | abo | floor_lamp | every style family it fits already has 3 models of its type: rank 14: floor_lamp already has 3 models of each of its styles (modern minimal, minimal, modern) |
| abo_B07MF1V33V | abo | table_dining | every style family it fits already has 3 models of its type: rank 20: table_dining already has 3 models of each of its styles (scandinavian, minimal, modern) |
| abo_B07ML7P94G | abo | table_dining | every style family it fits already has 3 models of its type: rank 21: table_dining already has 3 models of each of its styles (scandinavian, japandi, minimal, modern, rustic) |
| abo_B07ML7PPZC | abo | floor_lamp | every style family it fits already has 3 models of its type: rank 21: floor_lamp already has 3 models of each of its styles (modern minimal, minimal, modern) |
| abo_B07PMK78R8 | abo | bookshelf | every style family it fits already has 3 models of its type: rank 15: bookshelf already has 3 models of each of its styles (modern minimal, minimal, modern) |
| abo_B07PNHSR4G | abo | bookshelf | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B07PPNNCM2 | abo | bookshelf | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B07PQS58XN | abo | bookshelf | every style family it fits already has 3 models of its type: rank 19: bookshelf already has 3 models of each of its styles (modern minimal, minimal, modern) |
| abo_B07PSZHDNK | abo | bookshelf | every style family it fits already has 3 models of its type: rank 16: bookshelf already has 3 models of each of its styles (modern minimal, minimal, modern) |
| abo_B07PVBJ7X8 | abo | dresser | every style family it fits already has 3 models of its type: rank 13: dresser already has 3 models of each of its styles (modern minimal, minimal, modern) |
| abo_B07PVL2N3D | abo | desk | every style family it fits already has 3 models of its type: rank 15: desk already has 3 models of each of its styles (modern minimal, industrial) |
| abo_B07PX3CC31 | abo | nightstand | every style family it fits already has 3 models of its type: rank 15: nightstand already has 3 models of each of its styles (modern minimal, minimal) |
| abo_B07PXFVNXR | abo | dresser | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B07PYKLXGB | abo | dresser | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B07PYKPBY9 | abo | dresser | every style family it fits already has 3 models of its type: rank 16: dresser already has 3 models of each of its styles (modern minimal, minimal, modern) |
| abo_B07PYT7NZ9 | abo | desk | every style family it fits already has 3 models of its type: rank 22: desk already has 3 models of each of its styles (modern minimal) |
| abo_B07PYYRV2L | abo | desk | every style family it fits already has 3 models of its type: rank 19: desk already has 3 models of each of its styles (modern minimal, industrial) |
| abo_B07Q44L76B | abo | armchair | over the per-type limit of the catalogue: rank 29 of 36 accepted armchair models (keep 12) |
| abo_B07QB8DQ45 | abo | tv_unit | every style family it fits already has 3 models of its type: rank 16: tv_unit already has 3 models of each of its styles (japandi, modern) |
| abo_B07QB8L7YC | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm False |
| abo_B07QC84LTR | abo | desk | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B07QD6TXWS | abo | nightstand | every style family it fits already has 3 models of its type: rank 6: nightstand already has 3 models of each of its styles (scandinavian, modern minimal, minimal, modern) |
| abo_B07QD6ZDDH | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm False |
| abo_B07QF9QCZ1 | abo | tv_unit | every style family it fits already has 3 models of its type: rank 5: tv_unit already has 3 models of each of its styles (japandi) |
| abo_B07QFB1TLZ | abo | table_coffee | every style family it fits already has 3 models of its type: rank 15: table_coffee already has 3 models of each of its styles (scandinavian, japandi, modern minimal, minimal, modern) |
| abo_B07QFB4LWJ | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm False |
| abo_B07QFB5H65 | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm False |
| abo_B07QGFYLLM | abo | side_table | over the per-type limit of the catalogue: rank 21 of 23 accepted side_table models (keep 12) |
| abo_B07QGWMTDY | abo | table_dining | every style family it fits already has 3 models of its type: rank 11: table_dining already has 3 models of each of its styles (scandinavian, japandi, modern minimal, minimal, modern) |
| abo_B07QM1WB1J | abo | bed_single | not the furniture type (a judge): qwen False, glm False |
| abo_B07QS8TBXT | abo | nightstand | every style family it fits already has 3 models of its type: rank 16: nightstand already has 3 models of each of its styles (modern minimal, minimal) |
| abo_B07QTB45S5 | abo | bookshelf | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| abo_B07QTD914H | abo | chair | over the per-type limit of the catalogue: rank 27 of 38 accepted chair models (keep 12) |
| abo_B07QTKCKVB | abo | desk | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| abo_B07QV37J6B | abo | desk | every style family it fits already has 3 models of its type: rank 16: desk already has 3 models of each of its styles (modern minimal, industrial) |
| abo_B07R3TWDTM | abo | sofa | over the per-type limit of the catalogue: rank 26 of 36 accepted sofa models (keep 12) |
| abo_B07R6TND49 | abo | bed_single | front not agreed (judges and geometry or the documented front): judges: view 2 (+Y); documented front -Y (ABO convention (3dmodels/README.md): glTF +Z points to the product's natural front = -Y in the importer's Z-up frame) |
| abo_B07R7XFD22 | abo | bed_double | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| abo_B07R8WD99Z | abo | table_coffee | every style family it fits already has 3 models of its type: rank 23: table_coffee already has 3 models of each of its styles (modern minimal, minimal) |
| abo_B07RMZ8B11 | abo | tv_unit | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| abo_B07RNZC4TJ | abo | nightstand | every style family it fits already has 3 models of its type: rank 13: nightstand already has 3 models of each of its styles (scandinavian, modern minimal, minimal, modern) |
| abo_B07RPZSM4W | abo | nightstand | every style family it fits already has 3 models of its type: rank 9: nightstand already has 3 models of each of its styles (scandinavian, japandi, modern minimal, minimal, modern) |
| abo_B07RVBMJB8 | abo | side_table | over the per-type limit of the catalogue: rank 22 of 23 accepted side_table models (keep 12) |
| abo_B07RVBPWG9 | abo | desk | every style family it fits already has 3 models of its type: rank 10: desk already has 3 models of each of its styles (modern minimal, industrial) |
| abo_B07SB8WWHD | abo | tv_unit | every style family it fits already has 3 models of its type: rank 18: tv_unit already has 3 models of each of its styles (modern minimal, minimal) |
| abo_B07SJ75Y1M | abo | table_dining | every style family it fits already has 3 models of its type: rank 13: table_dining already has 3 models of each of its styles (scandinavian, japandi, modern minimal, minimal, modern) |
| abo_B07SQ9P548 | abo | table_coffee | every style family it fits already has 3 models of its type: rank 17: table_coffee already has 3 models of each of its styles (modern minimal, minimal) |
| abo_B07TF9MY62 | abo | chair | every style family it fits already has 3 models of its type: rank 20: chair already has 3 models of each of its styles (modern minimal, modern) |
| abo_B07VDD563W | abo | table_dining | every style family it fits already has 3 models of its type: rank 16: table_dining already has 3 models of each of its styles (scandinavian, modern minimal, minimal, modern) |
| abo_B07W5648MH | abo | side_table | every style family it fits already has 3 models of its type: rank 13: side_table already has 3 models of each of its styles (modern minimal, minimal, modern) |
| abo_B07ZVLRCSG | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm False |
| abo_B07ZVM6QMT | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm False |
| abo_B07ZVMQ9B9 | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm False |
| abo_B0824DVF9J | abo | floor_lamp | every style family it fits already has 3 models of its type: rank 15: floor_lamp already has 3 models of each of its styles (modern minimal, modern) |
| abo_B0824F3KWB | abo | floor_lamp | every style family it fits already has 3 models of its type: rank 22: floor_lamp already has 3 models of each of its styles (minimal, modern) |
| abo_B0824F7ZLF | abo | floor_lamp | every style family it fits already has 3 models of its type: rank 13: floor_lamp already has 3 models of each of its styles (minimal, modern) |
| abo_B0825D7RYW | abo | floor_lamp | every style family it fits already has 3 models of its type: rank 24: floor_lamp already has 3 models of each of its styles (modern minimal, minimal, modern) |
| abo_B082JGV1YM | abo | bookshelf | every style family it fits already has 3 models of its type: rank 17: bookshelf already has 3 models of each of its styles (modern) |
| abo_B082VSLQBK | abo | side_table | over the per-type limit of the catalogue: rank 23 of 23 accepted side_table models (keep 12) |
| abo_B082VSXML3 | abo | table_dining | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| abo_B082VT4GGJ | abo | side_table | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| abo_B083YFL4D7 | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm True |
| abo_B083YFL9JB | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm False |
| abo_B083YFPZ7X | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm False |
| abo_B083YFS2FR | abo | plant | not the decor type (a judge; a planter must hold a plant): qwen False, glm False |
| abo_B084QWW4LR | abo | tv_unit | every style family it fits already has 3 models of its type: rank 22: tv_unit already has 3 models of each of its styles (japandi, modern minimal, modern) |
| abo_B084RZVHD2 | abo | chair | every style family it fits already has 3 models of its type: rank 17: chair already has 3 models of each of its styles (scandinavian, japandi, modern minimal, minimal, modern) |
| abo_B084T7MQB4 | abo | chair | over the per-type limit of the catalogue: rank 26 of 38 accepted chair models (keep 12) |
| abo_B084W2DDSG | abo | chair | every style family it fits already has 3 models of its type: rank 19: chair already has 3 models of each of its styles (modern minimal, minimal, modern) |
| abo_B084W2GNQW | abo | chair | every style family it fits already has 3 models of its type: rank 16: chair already has 3 models of each of its styles (modern minimal, minimal, modern) |
| abo_B084ZB8Z79 | abo | bed_double | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| abo_B084ZBDPG5 | abo | bed_double | every style family it fits already has 3 models of its type: rank 12: bed_double already has 3 models of each of its styles (modern minimal, minimal, modern) |
| abo_B084ZBX1YH | abo | bed_double | every style family it fits already has 3 models of its type: rank 15: bed_double already has 3 models of each of its styles (modern minimal, minimal) |
| abo_B0853Q3Z93 | abo | table_dining | not the furniture type (a judge): qwen False, glm True |
| abo_B085FGSHQH | abo | armchair | no style both judges name: qwen ['classic'], glm ['neutral'] |
| abo_B086VLRYXS | abo | bed_single | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| abo_B086VNNCMZ | abo | bed_double | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| aedb9509ef9347a5b055e02deeadeff7 | objaverse | armchair | every style family it fits already has 3 models of its type: rank 22: armchair already has 3 models of each of its styles (classic) |
| b05862a2023f4c02988b3bb3004f6ff6 | objaverse | desk | every style family it fits already has 3 models of its type: rank 13: desk already has 3 models of each of its styles (modern minimal, minimal, modern) |
| b0c0c9c65d06443c87391134a62e2287 | objaverse | table_coffee | every style family it fits already has 3 models of its type: rank 30: table_coffee already has 3 models of each of its styles (japandi, modern minimal, minimal, modern) |
| b1155b5ebd7c478bb0d35747c2211e5f | objaverse | sofa | over the per-type limit of the catalogue: rank 33 of 36 accepted sofa models (keep 12) |
| b2fefa6f7af04c18966655d68a458974 | objaverse | armchair | over the per-type limit of the catalogue: rank 36 of 36 accepted armchair models (keep 12) |
| b46803ba0bc64e12b31f832fb761c4e0 | objaverse | wardrobe | every style family it fits already has 3 models of its type: rank 13: wardrobe already has 3 models of each of its styles (scandinavian, modern minimal, minimal, modern) |
| b547d81073b64d3e97200fd3ae9a74af | objaverse | bed_single | every style family it fits already has 3 models of its type: rank 9: bed_single already has 3 models of each of its styles (scandinavian, japandi, modern minimal, minimal, modern) |
| b7f753028d354b419de1dcd966ab9f60 | objaverse | table_dining | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| b8792d1b3acf4081b0f173497d19d08b | objaverse | bookshelf | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry undecided (open_side: panel fractions {'-x': 0.0104, '+x': 0.0218, '-y': 0.0002, '+y': 0.0238} give 0 axes with one closed side) |
| b8c382798cdf473b86ed497a34770b35 | objaverse | chair | over the per-type limit of the catalogue: rank 34 of 38 accepted chair models (keep 12) |
| b930438e1f804c409fd9c3f5e4b01628 | objaverse | desk | every style family it fits already has 3 models of its type: rank 24: desk already has 3 models of each of its styles (modern minimal, minimal, modern) |
| baded4f3a22e4d6e9472e925e6f1fc12 | objaverse | bookshelf | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| bbe1d47c0d714884a66c53d6c1e5d177 | objaverse | table_coffee | every style family it fits already has 3 models of its type: rank 10: table_coffee already has 3 models of each of its styles (japandi, modern minimal, minimal, modern) |
| bcfae6acaa254778921933e9ca0f52b9 | objaverse | table_dining | every style family it fits already has 3 models of its type: rank 26: table_dining already has 3 models of each of its styles (scandinavian, modern minimal, minimal, modern) |
| bd384d46514548cf8c4202f1ae6ea551 | objaverse | fridge | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| be0c2264afaa496f9d2c4f09c528f14f | objaverse | table_dining | every style family it fits already has 3 models of its type: rank 25: table_dining already has 3 models of each of its styles (scandinavian, japandi, modern minimal, minimal, modern) |
| c00eb007075144949097e9ac78d483c3 | objaverse | toilet | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| c11f517d18d4494c8907c5a8f78f45a7 | objaverse | sofa | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| c1338e44401949c1be64e6668d38c100 | objaverse | potted_plant | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| c17577daa87849d09960669606c0ce27 | objaverse | table_coffee | every style family it fits already has 3 models of its type: rank 18: table_coffee already has 3 models of each of its styles (japandi, modern minimal, minimal, modern) |
| c1cbd15423b74c1a84517e6bc331d15f | objaverse | armchair | no style both judges name: qwen ['modern', 'minimal', 'scandinavian', 'japandi'], glm ['neutral'] |
| c42d069236174467a2fb536f7d42d7f0 | objaverse | table_coffee | every style family it fits already has 3 models of its type: rank 27: table_coffee already has 3 models of each of its styles (japandi, modern minimal, minimal, modern) |
| c4a92f9eafa64e03b8fe6e1c4ce462ab | objaverse | potted_plant | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| c5da9821e5684103bf0e6897c5c69b1e | objaverse | desk | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| c603a9922c6a4e77ab2306590f536ad6 | objaverse | armchair | over the per-type limit of the catalogue: rank 33 of 36 accepted armchair models (keep 12) |
| c626625486104768a6cab5eb4ecf9cf3 | objaverse | potted_plant | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| c66f09a20a9146ab9b004685a5a93787 | objaverse | desk | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| c67f61fa444044bcb88ec3e28f0ca7ac | objaverse | desk | front not agreed (judges and geometry or the documented front): judges: qwen 1, glm 3 |
| c6a248430aff4543aaa0e87b968c617a | objaverse | wardrobe | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry +Y |
| c7d79c5a304a476d87c8014a2f6565cf | objaverse | desk | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry +X |
| c83fd12998524dcab47e8127bb22dc00 | objaverse | stove | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry +Y |
| cb43e2abac66494d81e1e7116eb47043 | objaverse | chair | over the per-type limit of the catalogue: rank 30 of 38 accepted chair models (keep 12) |
| ce421f10e46d415198d5d19c5bd265f2 | objaverse | bookshelf | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| cf7f142c5aa8439d9b8d545993efdac4 | objaverse | toilet | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry undecided (back_taller: offsets +0.284 (x) and +0.147 (y) do not single out one axis) |
| d0f8edca337b43338674ca392f36c4df | objaverse | wardrobe | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| d1d7750af5144d1bb7d9fcc66b137c4c | objaverse | bed_single | front not agreed (judges and geometry or the documented front): judges: qwen 2, glm 0 |
| d26b667147a34c90b70fbeee399499fb | objaverse | wardrobe | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry undecided (detail_side: vertex counts {'-x': 3974, '+x': 4010, '-y': 2480, '+y': 2117} give no side with 1.3x more detail) |
| d367f2a1e96644c7afd46fdd47659a69 | objaverse | wardrobe | front not agreed (judges and geometry or the documented front): judges: view 0 (-Y); geometry undecided (detail_side: vertex counts {'-x': 851, '+x': 848, '-y': 95, '+y': 111} give no side with 1.3x more detail) |
| d48a42e91c5d4716a8c254addf8c9d99 | objaverse | bookshelf | every style family it fits already has 3 models of its type: rank 14: bookshelf already has 3 models of each of its styles (modern minimal, minimal, modern) |
| d584a1c6840949a8bad9d55e527e219b | objaverse | chair | over the per-type limit of the catalogue: rank 38 of 38 accepted chair models (keep 12) |
| d601c2907f114376bf9826272d686e81 | objaverse | chair | front not agreed (judges and geometry or the documented front): judges: view 2 (+Y); geometry undecided (back_taller: offsets -0.167 (x) and -0.296 (y) do not single out one axis) |
| d7fcaa3e8c844418a38b721c325bb2af | objaverse | bed_single | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| da6d646358d1451fa751f1a9141290a3 | objaverse | armchair | every style family it fits already has 3 models of its type: rank 10: armchair already has 3 models of each of its styles (classic) |
| dc16ef2fe078419fa8eae914c06d2080 | objaverse | potted_plant | not the furniture type (a judge): qwen False, glm True |
| dda2613eb5c04527a325a3b0bce9f79c | objaverse | bed_single | front not agreed (judges and geometry or the documented front): judges: view 1 (+X); geometry undecided (back_taller: top centroid offset -0.006 of the extent on y is below 0.08: no taller side) |
| dfb7c3b51e264b5083dc28450e55c2a0 | objaverse | chair | front not agreed (judges and geometry or the documented front): judges: qwen 0, glm 3 |
| e1ebf58bb90d4ea6b2a9643bfef9ecf8 | objaverse | floor_lamp | every style family it fits already has 3 models of its type: rank 29: floor_lamp already has 3 models of each of its styles (classic) |
| e4a1aafed0ec43a79c20f91dfcfe5670 | objaverse | stove | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| e9f40d803a874e84931192f09dedd58b | objaverse | desk | front not agreed (judges and geometry or the documented front): judges: view 3 (-X); geometry +Y |
| ea1ea4d5847b4550bc58ef4107df6f94 | objaverse | fridge | front not agreed (judges and geometry or the documented front): judges: qwen 1, glm 0 |
| ea5d7b8656c74af3843a5fcb34c30d21 | objaverse | bed_double | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| eadfe8fe43124205b2551635252f9e8c | objaverse | potted_plant | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| eb8faa54b7684e18abe6af39e1526b7b | objaverse | wardrobe | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| ebed0a3af94242a6be6bf0f8ed6cd49d | objaverse | armchair | over the per-type limit of the catalogue: rank 32 of 36 accepted armchair models (keep 12) |
| ed62e8ab9bd241038609d48a26388b16 | objaverse | desk | not a single object (a judge): qwen False, glm True |
| ef3832963ab24d129ec88fd4cac4818f | objaverse | sofa | over the per-type limit of the catalogue: rank 27 of 36 accepted sofa models (keep 12) |
| f04d12dd1e5444109f860c78679fafc0 | objaverse | armchair | no style both judges name: qwen ['classic'], glm ['neutral'] |
| f0ff385edd4f4a9ebac56d755c2f6634 | objaverse | sofa | front not agreed (judges and geometry or the documented front): judges: qwen 1, glm 3 |
| f1b05ddf1b634481903e353d41b6a654 | objaverse | bathtub | front not agreed (judges and geometry or the documented front): judges: view 1 (+X); geometry -X |
| f2b3a71f48d040069fb144f76a1180d9 | objaverse | bed_double | not the furniture type (a judge): qwen False, glm True |
| f4a50b61cf154b01a184c117a27ec348 | objaverse | floor_lamp | over the per-type limit of the catalogue: rank 31 of 31 accepted floor_lamp models (keep 12) |
| f57bb579c5da4b9c95f1cb874ec558f7 | objaverse | fridge | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| f7f99449b896488fa6d468e70518b21d | objaverse | armchair | over the per-type limit of the catalogue: rank 31 of 36 accepted armchair models (keep 12) |
| fd612e2ea8e94d80ac3b8097eb2e5bbe | objaverse | bathtub | front not agreed (judges and geometry or the documented front): judges: qwen 2, glm 3 |
| fe4339a62a544ec081d23f85e1a8c7f7 | objaverse | stove | photoreal quality below 4 (a judge): qwen 3, glm 4 |
