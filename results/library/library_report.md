# Objaverse furniture library (docs/milestone7.md §7)

Contains information from Objaverse 1.0 (https://huggingface.co/datasets/allenai/objaverse, revision 21e4e14), which is made available under the ODC Attribution License (ODC-By 1.0, https://opendatacommons.org/licenses/by/1-0/). Every object keeps its own licence (here CC0 1.0 or CC BY 4.0), as declared by its uploader and not verified by WenArt_RUN: check it before commercial use. This file is licensed ODC-By 1.0, not MIT.

Dataset: [allenai/objaverse](https://huggingface.co/datasets/allenai/objaverse) @ `21e4e14` (ODC-By-1.0). Licence strings and metadata field names of objaverse.yaml verified on the pod: yes.

## Steps

| Step | Objects |
|---|---|
| LVIS objects in the mapped categories | 1498 |
| Licence CC0 or CC BY 4.0 (metadata) | 1370 |
| Past the metadata prefilter (credit, faces, size) | 858 |
| Candidates (downloaded; textured or vertex-coloured) | 127 |
| Rendered (thumbnails) | 127 |
| Ready for judging (unit and type resolved) | 113 |
| of which normalised by type (model units unknown) | 73 |
| Judged by both models | 113 |
| Accepted | 50 |
| In catalog_objaverse.json | 50 |

## Per type (bed candidates are split into bed_single / bed_double after the unit guess)

| Type | LVIS | CC0/CC BY | Candidates | Ready | Accepted | In catalogue |
|---|---|---|---|---|---|---|
| armchair | 97 | 84 | 8 | 8 | 6 | 6 |
| bathtub | 30 | 26 | 8 | 6 | 0 | 0 |
| bed_double | – | – | – | 8 | 3 | 3 |
| bed_double|bed_single | 53 | 51 | 16 | 0 | 0 | 0 |
| bed_single | – | – | – | 7 | 2 | 2 |
| bookshelf | 103 | 100 | 8 | 6 | 3 | 3 |
| chair | 453 | 444 | 8 | 8 | 5 | 5 |
| desk | 76 | 74 | 7 | 7 | 1 | 1 |
| floor_lamp | 79 | 76 | 8 | 6 | 4 | 4 |
| fridge | 55 | 48 | 8 | 8 | 2 | 2 |
| potted_plant | 81 | 79 | 8 | 8 | 2 | 2 |
| sofa | 81 | 73 | 8 | 7 | 5 | 5 |
| stove | 35 | 31 | 7 | 5 | 1 | 1 |
| table_coffee | 51 | 49 | 8 | 6 | 5 | 5 |
| table_dining | 70 | 67 | 8 | 6 | 4 | 4 |
| toilet | 111 | 52 | 7 | 7 | 3 | 3 |
| wardrobe | 97 | 93 | 8 | 8 | 3 | 3 |
| washbasin | 26 | 23 | 2 | 2 | 1 | 1 |

## Refusals by reason (first failed rule per object)

| Step | Code | Reason | Objects |
|---|---|---|---|
| survey | face_count | face count outside 2k-150k | 486 |
| survey | glb_size | GLB larger than 40 MB | 26 |
| survey | licence_refused | licence not CC0 / CC BY 4.0 (NC, ND, SA, Standard, Editorial) | 128 |
| survey | untextured | no image texture and no vertex colours | 67 |
| survey | not_selected | below the top 8 per type (rank by likes, views) | 664 |
| thumbnails | over_candidate_limit | over the 8 candidates of its type after the bed split | 1 |
| thumbnails | unit_none | no unit factor fits and the box proportions (footprint, height / width) are outside the type's ranges | 13 |
| accept | front_not_agreed | front not agreed (judges and geometry) | 33 |
| accept | no_common_style | no style both judges name | 1 |
| accept | over_type_limit | over the per-type limit of the catalogue | 2 |
| accept | quality | photoreal quality below 4 (a judge) | 23 |
| accept | type_mismatch | not the furniture type (a judge) | 4 |

## Licence values seen (metadata field `license`)

| Value | Objects | Decision |
|---|---|---|
| `by` | 1369 | CC-BY-4.0 |
| `by-sa` | 77 | licence_refused |
| `by-nc` | 35 | licence_refused |
| `by-nc-sa` | 16 | licence_refused |
| `cc0` | 1 | CC0 |

## LVIS categories

Found: `armchair` 97, `armoire` 58, `bathtub` 30, `bed` 53, `bookcase` 103, `chair` 453, `coffee_table` 51, `desk` 76, `dining_table` 70, `flowerpot` 81, `lamp` 79, `refrigerator` 55, `sink` 26, `sofa` 81, `stove` 35, `toilet` 111, `wardrobe` 39.
Missing (a warning: their types stay parametric): `chest_of_drawers_(furniture)`, `nightstand`.

- `chest_of_drawers_(furniture)`: names in the file sharing a word: `drawer` (an alternate needs a reason in objaverse.yaml).
- `nightstand`: names in the file sharing a word: `nightshirt` (an alternate needs a reason in objaverse.yaml).

## Style coverage

Models per type and style family: Objaverse + Poly Haven (`neutral` counts for every family; beds only with a mattress). `–` = no model: refit builds the parametric mesh for that pair.

| Type | scandinavian | japandi | modern minimal | minimal | modern | industrial | mediterranean | classic | rustic |
|---|---|---|---|---|---|---|---|---|---|
| bed_single | 2+0 | 2+0 | 2+0 | 2+0 | 2+0 | – | – | – | – |
| bed_double | 1+0 | 1+0 | 2+0 | 1+0 | 2+0 | 1+0 | – | 0+1 | – |
| sofa | – | – | 3+0 | – | 4+0 | – | – | 1+3 | – |
| armchair | – | – | 0+1 | 0+1 | 1+2 | – | – | 5+1 | – |
| table_dining | 2+0 | 1+0 | 2+0 | 2+0 | 3+0 | 1+0 | 1+0 | 1+0 | 2+3 |
| table_coffee | 1+0 | 4+0 | 4+0 | 4+0 | 4+2 | – | – | 1+1 | 1+1 |
| desk | – | – | 1+0 | 1+0 | 1+0 | 0+2 | – | – | 0+1 |
| chair | 1+0 | 1+0 | 1+0 | 1+0 | 1+1 | 1+0 | – | 3+1 | 1+2 |
| wardrobe | 1+0 | – | 1+0 | 1+0 | 1+0 | – | – | 2+0 | 1+0 |
| fridge | – | – | 2+0 | 2+0 | 2+0 | – | – | – | – |
| stove | 0+1 | 0+1 | 0+1 | 0+1 | 0+1 | 1+1 | 0+1 | 0+1 | 0+1 |
| washbasin | – | – | 1+0 | 1+0 | 1+0 | – | – | – | – |
| toilet | – | – | 3+0 | 3+0 | 3+0 | – | – | – | – |
| bathtub | – | – | – | – | – | – | – | – | – |
| bookshelf | 1+1 | 1+1 | 2+1 | 2+1 | 1+1 | 1+0 | 1+0 | 2+0 | 1+2 |
| nightstand | 0+1 | 0+1 | 0+1 | 0+1 | 0+1 | – | – | 0+1 | 0+1 |
| dresser | – | – | – | – | – | – | – | 0+2 | – |
| floor_lamp | – | – | – | – | 2+0 | 1+0 | – | 2+0 | – |
| potted_plant | – | – | – | – | – | – | 1+0 | – | 1+0 |

Parametric: 77 of 171 type/family pairs.

## Catalogue

| Type | Id | Title | Author | Licence | Styles | Front | Quality | W x D x H (m) | Unit |
|---|---|---|---|---|---|---|---|---|---|
| bed_single | `objaverse_6eb4212e70b941a3bd2db196a47828b9` | Lowpoly Bed | Mohamed199 | CC-BY-4.0 | scandinavian, japandi, modern minimal, minimal, modern | -X (high) | 4/4 | 1.11 x 1.8 x 0.691 | x0.00535266 |
| bed_single | `objaverse_b547d81073b64d3e97200fd3ae9a74af` | Bed - Sample | Mifu Saja | CC-BY-4.0 | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 4/4 | 1 x 2.11 x 0.918 | x0.01 |
| bed_double | `objaverse_08f7f65edfea417b8ed9ca748381e507` | Bed | Ambriel | CC-BY-4.0 | scandinavian, japandi, modern minimal, minimal, modern | -X (high) | 5/4 | 2.43 x 2.12 x 0.9 | x0.001 |
| bed_double | `objaverse_2bd3fcc82c9f43cfb0c8cf26c7d0107c` | Bed For Vr | olamii | CC-BY-4.0 | modern minimal, modern | +X (high) | 4/4 | 1.75 x 1.96 x 1.5 | x0.000805333 |
| bed_double | `objaverse_5d3a99865ac84d8a8bf06b263aa5bb55` | Old Bed | barism09 | CC-BY-4.0 | industrial | -Y (high) | 4/4 | 1.47 x 2.55 x 1.4 | x0.01 |
| sofa | `objaverse_072d0468bb97447ab1ca7e3edea25f1f` | Day 195: Street Couch Pt.9 | alexdelker | CC-BY-4.0 | classic | -X (high) | 4/4 | 2.26 x 1.03 x 0.702 | x1 |
| sofa | `objaverse_42da0122f2134a189767d0911b401c1c` | Couch Gameready | elijahorama | CC-BY-4.0 | modern minimal, modern | -Y (high) | 4/4 | 2.16 x 0.899 x 0.707 | x1 |
| sofa | `objaverse_9b1e09abe5e34d6397937ebf59901898` | Modern Couch | Smitty__Werben | CC-BY-4.0 | modern minimal, modern | -Y (high) | 4/4 | 2.75 x 0.891 x 0.818 | x1 |
| sofa | `objaverse_9c242421a7c1447f941f72b57e7473e5` | SOFA COUCH | Samiix3D | CC-BY-4.0 | modern minimal, modern | -Y (high) | 4/4 | 2.17 x 0.869 x 0.981 | x0.400319 |
| sofa | `objaverse_ef3832963ab24d129ec88fd4cac4818f` | Arno_Blush_Velvet_Sofa_HP | Vitor.GomesPT | CC-BY-4.0 | modern | -Y (high) | 4/4 | 2 x 0.905 x 0.711 | x1 |
| armchair | `objaverse_09ee59423b4b428f94f01fc5beccd227` | Old Sofa | Batuhan13 | CC-BY-4.0 | classic | -Y (high) | 5/4 | 0.761 x 0.95 x 1.11 | x0.00215423 |
| armchair | `objaverse_124297e7e4574c48b9c1b814b6ddf516` | animated_sphere | ferhatsen | CC-BY-4.0 | classic | -Y (high) | 5/5 | 0.751 x 0.84 x 0.91 | x1 |
| armchair | `objaverse_69f1c0489a144f3c98e66dcfe72b3969` | Oldfashioned armchair | yezzyx | CC-BY-4.0 | classic | -Y (high) | 5/5 | 0.533 x 0.612 x 0.613 | x0.0254 |
| armchair | `objaverse_aedb9509ef9347a5b055e02deeadeff7` | Sofa | mustafasahinfb | CC-BY-4.0 | classic | +X (high) | 4/5 | 0.902 x 0.901 x 0.943 | x0.01 |
| armchair | `objaverse_da6d646358d1451fa751f1a9141290a3` | LPUVW | HannaPachurka | CC-BY-4.0 | classic | -Y (high) | 5/5 | 0.533 x 0.612 x 0.613 | x0.0254 |
| armchair | `objaverse_f7f99449b896488fa6d468e70518b21d` | Purple Armchair | Olena_Skrypka | CC-BY-4.0 | modern | -Y (high) | 4/4 | 0.976 x 0.741 x 0.887 | x0.0883862 |
| table_dining | `objaverse_3b4ee19c627e4fb4a3305621cf925aa2` | Dining Set | dan2211082 | CC-BY-4.0 | rustic, neutral | -Y (low) | 4/5 | 1.31 x 1.23 x 0.704 | x0.0077457 |
| table_dining | `objaverse_5847113c458f4a2483aedd663376c7de` | Dining Table Set | Jainesh Pathak | CC-BY-4.0 | minimal, modern | -Y (low) | 4/4 | 1.32 x 2.15 x 0.65 | x0.0019697 |
| table_dining | `objaverse_5f235f066a9a416fb7177496a9117ec7` | Low Poly - Chair and Table | tadeus | CC-BY-4.0 | modern minimal, modern | -Y (low) | 4/4 | 1.7 x 1.07 x 0.65 | x0.00348235 |
| table_dining | `objaverse_724d93a7f3644f96909e8c55909c6418` | A table, chairs & few cups | Sahramin | CC-BY-4.0 | scandinavian, rustic | -Y (low) | 4/4 | 1.17 x 1.2 x 0.85 | x0.601997 |
| table_coffee | `objaverse_1d41e84fd76241e7a8929a314052269c` | LowPoly Industrial Tools vol. 1 | SANYABEAST | CC-BY-4.0 | scandinavian, japandi, modern minimal, minimal, modern | -Y (low) | 4/4 | 1.04 x 0.73 x 0.48 | x0.01 |
| table_coffee | `objaverse_b0c0c9c65d06443c87391134a62e2287` | Small Table | Pascal T. Monette | CC-BY-4.0 | japandi, modern minimal, minimal, modern | -Y (low) | 4/4 | 0.894 x 0.894 x 0.546 | x0.449913 |
| table_coffee | `objaverse_c17577daa87849d09960669606c0ce27` | Modern Table | Athlas | CC-BY-4.0 | japandi, modern minimal, minimal, modern | -Y (low) | 5/4 | 1.31 x 0.59 x 0.6 | x0.655745 |
| table_coffee | `objaverse_c42d069236174467a2fb536f7d42d7f0` | Coffee Shop Props | Brendan | CC-BY-4.0 | japandi, modern minimal, minimal, modern | -Y (low) | 4/4 | 0.894 x 0.894 x 0.432 | x0.298143 |
| table_coffee | `objaverse_f4031bb5f7e64ebca4c37d4fa5ba6e8d` | LP Table | doplerato | CC-BY-4.0 | classic, rustic | -Y (low) | 4/4 | 1.2 x 0.669 x 0.36 | x8.32595 |
| desk | `objaverse_b930438e1f804c409fd9c3f5e4b01628` | Red industrial desk | mhd.ayoub.chikhani | CC-BY-4.0 | modern minimal, minimal, modern | -Y (high) | 4/4 | 1.53 x 0.888 x 0.65 | x0.00237633 |
| chair | `objaverse_039c6026571943d6ac45c6816bcc7ff1` | Rocking Chair | Christian | CC-BY-4.0 | classic | -Y (high) | 5/5 | 0.41 x 0.609 x 0.822 | x0.657204 |
| chair | `objaverse_0723b35415b0462eb5c01140b6b70340` | Old chair | Dani Ortega | CC-BY-4.0 | classic | -Y (high) | 5/5 | 0.522 x 0.552 x 0.7 | x0.640063 |
| chair | `objaverse_9234d8196b73434684bcbb8092cc9e2a` | Victorian Chair | Jamie McFarlane | CC-BY-4.0 | classic | -X (high) | 4/4 | 0.467 x 0.536 x 0.931 | x0.46576 |
| chair | `objaverse_cb43e2abac66494d81e1e7116eb47043` | Vintage Chair | Maycho | CC-BY-4.0 | industrial, rustic | -Y (high) | 4/4 | 0.483 x 0.604 x 1.03 | x1 |
| chair | `objaverse_d2785b57e7da45858f2fe8bf4dedd68d` | Chair | 杭州维界科技有限公司 | CC-BY-4.0 | scandinavian, japandi, modern minimal, minimal, modern | -Y (high) | 5/5 | 0.517 x 0.503 x 0.829 | x0.01 |
| wardrobe | `objaverse_05a035c3347645b8a7ceb6d65f825ac3` | Dikkies Closet | klaxoneer | CC-BY-4.0 | classic | -Y (high) | 5/4 | 1.14 x 0.624 x 1.76 | x1 |
| wardrobe | `objaverse_b3a99e956be64ab6958f7f5e1895f031` | Warn Wardrobe | seenoise | CC-BY-4.0 | classic, rustic | -Y (high) | 4/4 | 1.29 x 0.564 x 2.31 | x1 |
| wardrobe | `objaverse_b46803ba0bc64e12b31f832fb761c4e0` | Simple Tall Shelf | Blender3D | CC-BY-4.0 | scandinavian, modern minimal, minimal, modern | -Y (high) | 4/4 | 1.05 x 0.563 x 2.6 | x0.118158 |
| fridge | `objaverse_2071bda681b642218b6829b82e4fd93b` | Refrigerator - Grey Polished Metal | Glowbox 3D | CC-BY-4.0 | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.766 x 0.661 x 1.54 | x0.193519 |
| fridge | `objaverse_68d69bbf7a454a09a2536ac0762532f3` | Old Fridge | golddog | CC-BY-4.0 | modern minimal, minimal, modern | +X (high) | 4/4 | 0.725 x 0.698 x 1.09 | x0.419674 |
| stove | `objaverse_7c5c9dec5c2e4ff998c386410b0e3686` | Stove | Daniyal Malik | CC-BY-4.0 | industrial | -X (high) | 4/4 | 0.592 x 0.71 x 0.867 | x0.00228858 |
| washbasin | `objaverse_ce1a06f7cbe1425099a145f851fc5dee` | Sink | Shining Salt | CC-BY-4.0 | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.649 x 0.476 x 0.55 | x0.324323 |
| toilet | `objaverse_0b3325fad3e740b1ac86173c90b56afd` | Toilettes | Lightningx | CC-BY-4.0 | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.462 x 0.621 x 0.839 | x0.0146675 |
| toilet | `objaverse_24d1b493899d407780140688abae19bc` | Toilet | Xill | CC-BY-4.0 | modern minimal, minimal, modern | -Y (high) | 4/4 | 0.453 x 0.633 x 0.801 | x0.744926 |
| toilet | `objaverse_3446229dce1f47528fa871cc7669136c` | Toilet | Ali107_YT | CC-BY-4.0 | modern minimal, minimal, modern | +X (high) | 4/4 | 0.453 x 0.634 x 0.761 | x0.0015794 |
| bookshelf | `objaverse_51d928b33e5549898cc86cbdaf966d83` | Simple Book Shelf | [FREE] | Agustin Honnun | Agustín Hönnun | CC-BY-4.0 | modern minimal, minimal | -Y (high) | 4/4 | 1.2 x 0.419 x 1.99 | x1 |
| bookshelf | `objaverse_6c5ac2547db34c3c81b2e4808b000386` | Dusty Old Bookshelf (FREE) | Brandon Westlake | CC-BY-4.0 | classic | +Y (high) | 4/4 | 0.92 x 0.387 x 2.08 | x1 |
| bookshelf | `objaverse_b43c45317fd74a4aa9ba443b9a355ea3` | Bookcase | Icanreed | CC-BY-4.0 | modern, neutral | -Y (high) | 5/4 | 1.05 x 0.434 x 1.92 | x0.348837 |
| floor_lamp | `objaverse_01c53767c1f84f55ad9f46eb89949cf9` | Street Lamp | emelyarules | CC-BY-4.0 | classic | -Y (low) | 4/4 | 0.332 x 0.381 x 2.1 | x0.61174 |
| floor_lamp | `objaverse_33eb258d9873435690254cfbb0ea46ec` | Floor Lamp | bilgehan.korkmaz | CC-BY-4.0 | modern | -Y (low) | 4/5 | 0.517 x 0.517 x 2 | x1 |
| floor_lamp | `objaverse_71853da424aa4b208e14f6cf430339ae` | Street lights | U-like | CC-BY-4.0 | industrial, classic | -Y (low) | 5/4 | 0.349 x 0.349 x 2.1 | x1.74412 |
| floor_lamp | `objaverse_8170cf1409924abc9c3fc8becccdd36e` | Lamp - WIP | KeenanBabcock | CC-BY-4.0 | modern | -Y (low) | 4/4 | 0.425 x 0.425 x 1.34 | x0.0757288 |
| potted_plant | `objaverse_71b53eaee72e4a829a9256a7bcfb7dab` | Cacti pot | Spacyy | CC-BY-4.0 | rustic | -Y (low) | 4/4 | 0.222 x 0.234 x 0.305 | x0.0254 |
| potted_plant | `objaverse_b99c584dd11d4691b5d13303383371e5` | FlowerPot | ibrahmcingi | CC-BY-4.0 | mediterranean | -Y (low) | 4/4 | 0.6 x 0.6 x 0.58 | x0.0027579 |

## Attribution

Contains information from Objaverse 1.0 (https://huggingface.co/datasets/allenai/objaverse, revision 21e4e14), which is made available under the ODC Attribution License (ODC-By 1.0, https://opendatacommons.org/licenses/by/1-0/). Every object keeps its own licence (here CC0 1.0 or CC BY 4.0), as declared by its uploader and not verified by WenArt_RUN: check it before commercial use. This file is licensed ODC-By 1.0, not MIT.

- "Lowpoly Bed" by Mohamed199 (https://sketchfab.com/3d-models/6eb4212e70b941a3bd2db196a47828b9), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Bed - Sample" by Mifu Saja (https://sketchfab.com/3d-models/b547d81073b64d3e97200fd3ae9a74af), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Bed" by Ambriel (https://sketchfab.com/3d-models/08f7f65edfea417b8ed9ca748381e507), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Bed For Vr" by olamii (https://sketchfab.com/3d-models/2bd3fcc82c9f43cfb0c8cf26c7d0107c), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Old Bed" by barism09 (https://sketchfab.com/3d-models/5d3a99865ac84d8a8bf06b263aa5bb55), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Day 195: Street Couch Pt.9" by alexdelker (https://sketchfab.com/3d-models/072d0468bb97447ab1ca7e3edea25f1f), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Couch Gameready" by elijahorama (https://sketchfab.com/3d-models/42da0122f2134a189767d0911b401c1c), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Modern Couch" by Smitty__Werben (https://sketchfab.com/3d-models/9b1e09abe5e34d6397937ebf59901898), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "SOFA COUCH" by Samiix3D (https://sketchfab.com/3d-models/9c242421a7c1447f941f72b57e7473e5), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Arno_Blush_Velvet_Sofa_HP" by Vitor.GomesPT (https://sketchfab.com/3d-models/ef3832963ab24d129ec88fd4cac4818f), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Old Sofa" by Batuhan13 (https://sketchfab.com/3d-models/09ee59423b4b428f94f01fc5beccd227), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "animated_sphere" by ferhatsen (https://sketchfab.com/3d-models/124297e7e4574c48b9c1b814b6ddf516), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Oldfashioned armchair" by yezzyx (https://sketchfab.com/3d-models/69f1c0489a144f3c98e66dcfe72b3969), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Sofa" by mustafasahinfb (https://sketchfab.com/3d-models/aedb9509ef9347a5b055e02deeadeff7), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "LPUVW" by HannaPachurka (https://sketchfab.com/3d-models/da6d646358d1451fa751f1a9141290a3), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Purple Armchair" by Olena_Skrypka (https://sketchfab.com/3d-models/f7f99449b896488fa6d468e70518b21d), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Dining Set" by dan2211082 (https://sketchfab.com/3d-models/3b4ee19c627e4fb4a3305621cf925aa2), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Dining Table Set" by Jainesh Pathak (https://sketchfab.com/3d-models/5847113c458f4a2483aedd663376c7de), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Low Poly - Chair and Table" by tadeus (https://sketchfab.com/3d-models/5f235f066a9a416fb7177496a9117ec7), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "A table, chairs & few cups" by Sahramin (https://sketchfab.com/3d-models/724d93a7f3644f96909e8c55909c6418), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "LowPoly Industrial Tools vol. 1" by SANYABEAST (https://sketchfab.com/3d-models/1d41e84fd76241e7a8929a314052269c), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Small Table" by Pascal T. Monette (https://sketchfab.com/3d-models/b0c0c9c65d06443c87391134a62e2287), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Modern Table" by Athlas (https://sketchfab.com/3d-models/c17577daa87849d09960669606c0ce27), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Coffee Shop Props" by Brendan (https://sketchfab.com/3d-models/c42d069236174467a2fb536f7d42d7f0), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "LP Table" by doplerato (https://sketchfab.com/3d-models/f4031bb5f7e64ebca4c37d4fa5ba6e8d), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Red industrial desk" by mhd.ayoub.chikhani (https://sketchfab.com/3d-models/b930438e1f804c409fd9c3f5e4b01628), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Rocking Chair" by Christian (https://sketchfab.com/3d-models/039c6026571943d6ac45c6816bcc7ff1), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Old chair" by Dani Ortega (https://sketchfab.com/3d-models/0723b35415b0462eb5c01140b6b70340), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Victorian Chair" by Jamie McFarlane (https://sketchfab.com/3d-models/9234d8196b73434684bcbb8092cc9e2a), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Vintage Chair" by Maycho (https://sketchfab.com/3d-models/cb43e2abac66494d81e1e7116eb47043), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Chair" by 杭州维界科技有限公司 (https://sketchfab.com/3d-models/d2785b57e7da45858f2fe8bf4dedd68d), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Dikkies Closet" by klaxoneer (https://sketchfab.com/3d-models/05a035c3347645b8a7ceb6d65f825ac3), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Warn Wardrobe" by seenoise (https://sketchfab.com/3d-models/b3a99e956be64ab6958f7f5e1895f031), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Simple Tall Shelf" by Blender3D (https://sketchfab.com/3d-models/b46803ba0bc64e12b31f832fb761c4e0), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Refrigerator - Grey Polished Metal" by Glowbox 3D (https://sketchfab.com/3d-models/2071bda681b642218b6829b82e4fd93b), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Old Fridge" by golddog (https://sketchfab.com/3d-models/68d69bbf7a454a09a2536ac0762532f3), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Stove" by Daniyal Malik (https://sketchfab.com/3d-models/7c5c9dec5c2e4ff998c386410b0e3686), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Sink" by Shining Salt (https://sketchfab.com/3d-models/ce1a06f7cbe1425099a145f851fc5dee), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Toilettes" by Lightningx (https://sketchfab.com/3d-models/0b3325fad3e740b1ac86173c90b56afd), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Toilet" by Xill (https://sketchfab.com/3d-models/24d1b493899d407780140688abae19bc), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Toilet" by Ali107_YT (https://sketchfab.com/3d-models/3446229dce1f47528fa871cc7669136c), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Simple Book Shelf | [FREE] | Agustin Honnun" by Agustín Hönnun (https://sketchfab.com/3d-models/51d928b33e5549898cc86cbdaf966d83), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Dusty Old Bookshelf (FREE)" by Brandon Westlake (https://sketchfab.com/3d-models/6c5ac2547db34c3c81b2e4808b000386), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Bookcase" by Icanreed (https://sketchfab.com/3d-models/b43c45317fd74a4aa9ba443b9a355ea3), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Street Lamp" by emelyarules (https://sketchfab.com/3d-models/01c53767c1f84f55ad9f46eb89949cf9), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Floor Lamp" by bilgehan.korkmaz (https://sketchfab.com/3d-models/33eb258d9873435690254cfbb0ea46ec), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Street lights" by U-like (https://sketchfab.com/3d-models/71853da424aa4b208e14f6cf430339ae), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Lamp - WIP" by KeenanBabcock (https://sketchfab.com/3d-models/8170cf1409924abc9c3fc8becccdd36e), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "Cacti pot" by Spacyy (https://sketchfab.com/3d-models/71b53eaee72e4a829a9256a7bcfb7dab), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched
- "FlowerPot" by ibrahmcingi (https://sketchfab.com/3d-models/b99c584dd11d4691b5d13303383371e5), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched

## Refused after judging

| uid | Type | Reason |
|---|---|---|
| 01b79647e6e442989fda47ff20cabdc9 | armchair | over the per-type limit of the catalogue: rank 8 of 8 accepted armchair models (keep 6) |
| 132a8ee2af3a40d39d270fbed3d3666c | toilet | front not agreed (judges and geometry): judges: qwen 1, glm 0 |
| 15a583ac9db84a529e7ea1d2bd7eadbe | fridge | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| 17c796aeb1b8455d8f594a72490e11b7 | washbasin | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 1f07c148a7bc4e7c88dc57de50dc36b3 | toilet | front not agreed (judges and geometry): judges: view 0 (-Y); geometry undecided (back_taller: offsets -0.057 (x) and +0.092 (y) do not single out one axis) |
| 23fa151346304c8bb8c58f58a76e6407 | desk | front not agreed (judges and geometry): judges: qwen 1, glm 3 |
| 2b7d5c96159c42589dd970d81e877668 | toilet | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 2f1706233a3248cf9a74586fc2e7120c | bathtub | front not agreed (judges and geometry): judges: qwen 2, glm 0 |
| 309ccba7b2cb40a6bfffb89f498fc54c | wardrobe | front not agreed (judges and geometry): judges: view 0 (-Y); geometry undecided (detail_side: vertex counts {'-x': 96, '+x': 96, '-y': 50, '+y': 51} give no side with 1.3x more detail) |
| 317dac94ec404bdbaa6d41a85e04f51c | floor_lamp | not the furniture type (a judge): qwen False, glm True |
| 322ba3a159a845c7b7642467e23fcc2d | bed_single | front not agreed (judges and geometry): judges: qwen 1, glm 3 |
| 3597a7a470ac4f81b1b362eea66f4d6f | wardrobe | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 39541d5daa7a4fba9614ad9847c992d5 | desk | front not agreed (judges and geometry): judges: qwen 2, glm 0 |
| 426c14adba6a45638752986c2f7d16b2 | bed_double | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 4ae706aa53c043fa8261ebf40f580303 | potted_plant | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| 536dbfc2fdbe4dec9203ab390b9a6eda | bathtub | front not agreed (judges and geometry): judges: qwen 2, glm 0 |
| 568f22034e364caca4e450a6d534dbd6 | bed_double | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| 592d31f4896948bb9ac5e53ac246d8c8 | stove | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| 5ec9697d85654005b27fd29bd6df987e | sofa | front not agreed (judges and geometry): judges: qwen 2, glm 0 |
| 604886640ac948f1980d81bc4a3ed7cf | bed_double | front not agreed (judges and geometry): judges: qwen 1, glm 0 |
| 624c9f7dcb2f4acd93237591ef10c76a | chair | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 65a13a04056c4f51a9c324e2a975b9a5 | bed_double | not the furniture type (a judge): qwen False, glm True |
| 674b6c07743e4f569d4b745949d1a0f1 | bathtub | front not agreed (judges and geometry): judges: qwen 3, glm 2 |
| 70b7b418af714050aa83e99deb2253b7 | wardrobe | front not agreed (judges and geometry): judges: view 0 (-Y); geometry +Y |
| 75aa9519195647d99cf1e2d4863dbe87 | bookshelf | front not agreed (judges and geometry): judges: view 0 (-Y); geometry undecided (open_side: panel fractions {'-x': 0.8648, '+x': 0.8528, '-y': 0.0033, '+y': 0.0} give 0 axes with one closed side) |
| 774971f63ea54cdba8119439f4ff09c5 | table_dining | photoreal quality below 4 (a judge): qwen 3, glm 5 |
| 800d3c5569b94abfa2da7976504d589d | bathtub | front not agreed (judges and geometry): judges: view 0 (-Y); geometry +Y |
| 813f5aeef3f3430d947f3879c6941719 | floor_lamp | no style both judges name: qwen ['classic'], glm ['neutral'] |
| 815bd9cee3644f3f8996b4a6d123c7c3 | desk | front not agreed (judges and geometry): judges: qwen 2, glm 0 |
| 81ada0e24e1647d8a0d6d0708a696f84 | bed_single | front not agreed (judges and geometry): judges: qwen 2, glm 0 |
| 8cd4ef86c0914b95a181473230c77eda | stove | front not agreed (judges and geometry): judges: qwen 1, glm 0 |
| 8e1fddb38fa8400c9fcc784abe29aaaa | fridge | front not agreed (judges and geometry): judges: view 0 (-Y); geometry +Y |
| 8fba1e7048c0421fb7e6b6e8be8fce88 | stove | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 9155b2b4be5f452a98837459112a3b9b | potted_plant | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| 98b39c575de547a483f8fbaec2c0242f | potted_plant | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| 9c4935439367490b8039a3cad9c46243 | sofa | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| a5eea808dc20404cb5f9e05680f7362f | wardrobe | not the furniture type (a judge): qwen False, glm True |
| a82bff9b83be4072871d3e2afc6cec14 | fridge | front not agreed (judges and geometry): judges: view 0 (-Y); geometry +X |
| a9917037f0c643dbbde0475b59bc53b1 | table_coffee | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| aa9a7f23471a4bb6b461d5240c2bf1a7 | bookshelf | front not agreed (judges and geometry): judges: view 0 (-Y); geometry undecided (open_side: panel fractions {'-x': 0.2845, '+x': 0.2274, '-y': 0.0427, '+y': 0.1454} give 0 axes with one closed side) |
| b7f753028d354b419de1dcd966ab9f60 | table_dining | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| b8792d1b3acf4081b0f173497d19d08b | bookshelf | front not agreed (judges and geometry): judges: view 0 (-Y); geometry undecided (open_side: panel fractions {'-x': 0.0104, '+x': 0.0218, '-y': 0.0002, '+y': 0.0238} give 0 axes with one closed side) |
| bd384d46514548cf8c4202f1ae6ea551 | fridge | photoreal quality below 4 (a judge): qwen 4, glm 3 |
| c1338e44401949c1be64e6668d38c100 | potted_plant | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| c4a92f9eafa64e03b8fe6e1c4ce462ab | potted_plant | photoreal quality below 4 (a judge): qwen 3, glm 4 |
| c603a9922c6a4e77ab2306590f536ad6 | armchair | over the per-type limit of the catalogue: rank 7 of 8 accepted armchair models (keep 6) |
| c626625486104768a6cab5eb4ecf9cf3 | potted_plant | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| c67f61fa444044bcb88ec3e28f0ca7ac | desk | front not agreed (judges and geometry): judges: qwen 1, glm 3 |
| c7d79c5a304a476d87c8014a2f6565cf | desk | front not agreed (judges and geometry): judges: view 0 (-Y); geometry +X |
| cf7f142c5aa8439d9b8d545993efdac4 | toilet | front not agreed (judges and geometry): judges: view 0 (-Y); geometry undecided (back_taller: offsets +0.284 (x) and +0.147 (y) do not single out one axis) |
| d1d7750af5144d1bb7d9fcc66b137c4c | bed_single | front not agreed (judges and geometry): judges: qwen 2, glm 0 |
| d367f2a1e96644c7afd46fdd47659a69 | wardrobe | front not agreed (judges and geometry): judges: view 0 (-Y); geometry undecided (detail_side: vertex counts {'-x': 851, '+x': 848, '-y': 95, '+y': 111} give no side with 1.3x more detail) |
| d601c2907f114376bf9826272d686e81 | chair | front not agreed (judges and geometry): judges: view 2 (+Y); geometry undecided (back_taller: offsets -0.167 (x) and -0.296 (y) do not single out one axis) |
| d7fcaa3e8c844418a38b721c325bb2af | bed_single | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| dda2613eb5c04527a325a3b0bce9f79c | bed_single | front not agreed (judges and geometry): judges: view 1 (+X); geometry undecided (back_taller: top centroid offset -0.006 of the extent on y is below 0.08: no taller side) |
| dfb7c3b51e264b5083dc28450e55c2a0 | chair | front not agreed (judges and geometry): judges: qwen 0, glm 3 |
| e9f40d803a874e84931192f09dedd58b | desk | front not agreed (judges and geometry): judges: view 3 (-X); geometry +Y |
| ea1ea4d5847b4550bc58ef4107df6f94 | fridge | front not agreed (judges and geometry): judges: qwen 1, glm 0 |
| f1b05ddf1b634481903e353d41b6a654 | bathtub | front not agreed (judges and geometry): judges: view 1 (+X); geometry -X |
| f2b3a71f48d040069fb144f76a1180d9 | bed_double | not the furniture type (a judge): qwen False, glm True |
| f57bb579c5da4b9c95f1cb874ec558f7 | fridge | photoreal quality below 4 (a judge): qwen 3, glm 3 |
| fd612e2ea8e94d80ac3b8097eb2e5bbe | bathtub | front not agreed (judges and geometry): judges: qwen 2, glm 3 |
| fe4339a62a544ec081d23f85e1a8c7f7 | stove | photoreal quality below 4 (a judge): qwen 3, glm 4 |
