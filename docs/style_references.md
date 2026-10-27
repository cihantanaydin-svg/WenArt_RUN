# Style references: the AI learns what a good room looks like (27 Oct 2026)

User, 27 Oct 2026: "Rooms are not looking like the stylish rooms you can see in the internet, similarly veranda is
not like a veranda. Find a way that AI have an idea what is a good room looks like and try to make the rooms like
that ... take the good style photos from the internet and figure out what needs to be done to implement into the
project both for internal and external areas." Lesson UL42.

## 1. What is wrong now (real06, run 20261027-091638-full)

| Space | What a good photo of it shows | What our render has |
|---|---|---|
| Salon, 55 m² | rug under the seating, curtains, 2-3 art pieces, 2-3 plants, floor + table lamps lit, cushions and a throw, styled coffee table and shelves | 9 decor items, no rug (no coffee table, so no rug slot), no plant, no art, no lamp |
| Bedrooms | layered bedding, art over the bed, lamps on both nightstands, rug, curtains, a plant | 5-7 items; the AI's two passes disagree and drop the rest |
| Bathrooms | towels, mirror, plant, styled vanity, warm light | a ceiling light only (decor types allowed: mirror, blind, light, candle, basket) |
| Kitchen | stools, bowls, a board, plants, pendants | a blind and a pendant |
| Veranda, 22.8 m² | outdoor lounge or dining set, outdoor rug, planters, lanterns, cushions, a wood or stone floor | an empty paved slab under a light roof |
| Garden views | real trees, planted borders | lollipop trees, flat lawn |

The decor stage can build 21 decor types (curtains, blinds, throws, art, lamps, plants, rugs, ...): the problem is
that too few are asked for, the two AI passes must agree on each item, and nothing says what a good room of the type
and style holds. Outdoor spaces get no furniture or decor at all.

## 2. The way: reference photos -> recipe -> layers by code -> judged side by side

1. **Reference sets** (`wenart/style/references.py`): for each space in the project (living, bedroom, kitchen,
   bathroom, child, hall, dressing, veranda, terrace, balcony, garden, facade) and the project's style family (plus
   its fallback), the pod searches Creative Commons photographs (Openverse API, Wikimedia Commons; no key), keeps the
   10 best (SigLIP 2, Apache-2.0: a photo of the space, not a plan, render, product shot or empty room; style match
   and photo quality first; duplicates out). Cached on the network volume, reused by every project. Every photo keeps
   source, author, licence and page; `ATTRIBUTION.md` lists them; they are never rendered.
2. **Recipe** (`wenart/style/recipe.py`): the vision model reads each photo into a strict schema: which layers it
   shows (rug, curtains, art count, plants count, lamps, cushions, throw, styled surfaces, bedding, towels, accent
   wall, panelling; outdoors: lounge set, dining set, planters, outdoor rug, lanterns, pergola, cushions, climbing
   plants, decking), the palette, the density, signature items. Code aggregates: a layer in 60 % of the photos is a
   **must**, 30 % **often**, counts as medians. Cached per reference set. A built-in default recipe per space stands in
   until the pod has read the photos.
3. **Layers by code** (decor stage): the AI stylist gets the recipe ("good scandinavian living rooms show: ..."); every
   **must** layer the AI did not choose is added by code in a checked slot (no two-pass veto for must layers); a rug
   lies under every seating group (no coffee table needed); new decor types where the recipe needs them (towels, bath
   mat, kitchen accessories); lamps of the recipe are lit.
4. **Outdoor spaces furnished** (site stage): a veranda or terrace gets a lounge or dining group by its area and
   shape (library outdoor models, placed by the solver's rules: clear of doors, steps and the walkway), an outdoor
   rug, planters at the edges and columns, lanterns under the roof, a deck or stone floor look.
5. **Judged side by side** (judge, inspector, Argus): each render is shown with two reference photos of its space and
   style; the judge names the layers the reference has and the render lacks as typed findings (`missing_layer`) that
   route to the decor tools; Argus fixes them like any other finding.
6. **Measured** (report metric 18): SigLIP 2 similarity of each render to its reference set's centre and the photo
   quality score; before/after against the latest run. The big loop's house score includes it.

## 3. Order of work

| Step | What | Where | GPU |
|---|---|---|---|
| 1 | reference sets, recipes, default recipes | `wenart/style/references.py`, `recipe.py` | fetch + read on the pod (~5 min) |
| 2 | recipe-driven decor: must layers by code, rug under seating, towels / bath mat / kitchen items, lit lamps | `wenart/furniture/decor_ai.py`, `decor.py`, builders | - |
| 3 | outdoor groups on verandas and terraces | `wenart/blender/site.py`, `wenart/levels/outdoor.py`, fit | - |
| 4 | side-by-side judge, `missing_layer` findings to tools | `wenart/agent/judge.py`, causes, Argus | in the run |
| 5 | style similarity metric 18 | `wenart/report/metrics13.py` | in the run |
| 6 | pod run on real06, before/after | | ~$4.5 |

## 4. Network

The cloud session's proxy blocks api.openverse.org and commons.wikimedia.org (only huggingface.co answers), so the
pod fetches the photos. To look at the photos from the session too, add to the allow-list (docs/setup.md, step
4.1): `api.openverse.org`, `commons.wikimedia.org`, `upload.wikimedia.org`, `live.staticflickr.com`.

## 5. Built (27 Oct 2026)

| Part | Code | Test |
|---|---|---|
| reference sets: Openverse + Commons search, SigLIP 2 selection, cache, attribution, export, prefetch per project | `wenart/style/references.py` | `tests/test_style_references_20261027.py` |
| recipe schema, aggregation, gaps, built-in recipes, recipe text | `wenart/style/recipe.py` | same |
| reading the photos with the vision server, cached per set; a project's `recipes.json` | `wenart/style/recipe_read.py` | same |
| decor: the recipe in the stylist's question; must layers filled by code; a rug in front of a sofa without a coffee table and under a single bed; plants in kitchens and bathrooms | `wenart/furniture/decor_ai.py`, `decor.py` | same, `tests/test_decor_m8.py` |
| verandas and terraces: a lounge (or a smaller set) clear of doors, steps, columns and the walkway, planters, an outdoor rug, a lantern; outdoor models first in the fit | `wenart/furniture/outdoor_sets.py`, `fit.py` | `tests/test_outdoor_sets_20261027.py` |
| the judge sees the best reference photo of the view's space and names the missing layers | `wenart/agent/judge.py`, `loop.py` | `tests/test_style_references_20261027.py` |
| style similarity of every final render to its space's photos | `references.style_scores`, job step | same |
| pod job: prefetch after setup, recipes before the decor questions, scores and an export of the sets into the results | `scripts/jobs/full.sh`, `wenart/run/stages.py`, `scheduler.py` | `tests/test_run_stages.py` |

Replayed on run 20261027-091638-full's real06 building with the built-in recipes: the salon gets 15 decor items (was
9: rugs, curtains at every window, cushions, plants), the bedrooms 10 each, the veranda a sofa, a coffee table, two
armchairs, two planters, a rug and a lantern.

Next, from the first run with photos: hosts for the decor the rooms still lack (a coffee table and side tables in a
seating group, a console in the hall, the counter top in the kitchen, the vanity in the bathroom), towels and bath
mats, lit lamps, and metric 18 (the style similarity) in the report.

## 6. Where the photos come from now (27 Oct 2026)

The pod's Openverse and Commons searches returned nothing (runs 123917, 130756). User: "Find the photos yourself and
put it into the pod".

| Step | What | Where |
|---|---|---|
| 1 | search the captions of PD12M (Spawning/PD12M, 12.4 M public-domain and CC0 photos) for each space and the style family's words; no paintings, drawings, maps, old photos, photos under 1000 px | pod job `scripts/jobs/references.sh` (`references candidates`), hits cached on the volume |
| 2 | download up to 120 per space from the dataset's bucket (16 at a time), rank with SigLIP 2: a photo of a home's space, not a plan, render, product shot, empty room, public restroom, restaurant, museum room, showroom or painting; style and photo quality first | same |
| 3 | the best 30 per space come back as 512 px copies with a manifest | `runs/<job>/results/references_candidates/` |
| 4 | the session looks at them (numbered contact sheets) and keeps the homes of the space (up to 8) | `assets/references/<space>/<family>/` (in git; the rest of `assets/` stays ignored) |
| 5 | every run copies the committed sets to the volume first (a volume set with other photos gives way), reads their recipes with the vision model, and the judge sees the best one beside each render | `references prefetch`, `recipe_read`, `judge.reference_for` |

Picked (scandinavian, jobs 150744 and 160028, 92 photos, 3.6 MB): living 7, kitchen 8, bedroom 6, bathroom 8, dining
8, hall 1, veranda 8, terrace 8, balcony 6, garden 8, facade 8. Dressing and child room: no usable photo (a cloakroom,
museum rooms): their built-in recipes stand. Left out on sight: public restrooms, restaurants, hotel rooms, museum
period rooms, showrooms, Japanese gardens (not the family's look), near-duplicates of a picked photo.

## 7. Stylish photos from Pexels (27 Oct 2026)

User, 27 Oct 2026: "Find some better photos of the rooms, there should be some more stylish photos online." The
PD12M picks were museums, hotels and plain homes; the recipes read from them named shelves and plants but no rug,
curtains or lamps (run 160846). The photo job now searches CaptionEmporium/pexels-568k-internvl2 on the Hub (567,573
Pexels photos with title, tags, a detailed InternVL2 caption and the image address; Pexels License: free to use, no
attribution required, no resale of unaltered copies; the captions CC BY-SA 4.0): the space on the title and tags,
people and paintings out, ranked by the decor layers the caption names, then SigLIP 2. Job 175301 (5.4 min, $0.23)
returned 30 candidates for 12 spaces (child 10, dressing 7: mostly shops). Picked: living, kitchen, dining, bedroom,
bathroom, hall, veranda, terrace, garden, facade 8 each, balcony 7, child 6 (95 photos, 3.9 MB): light, wood, plants,
layered textiles, styled surfaces. They replace the PD12M picks. Dressing room: no usable photo (shops); its built-in
recipe stands. Unsplash's Lite data set was ruled out: mostly nature photos, and its terms forbid redistributing the
images.
