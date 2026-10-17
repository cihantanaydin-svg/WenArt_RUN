# Milestone 13 – realistic furniture, real vegetation, placement a designer accepts

Goal (user, 12 Oct 2026, prompt in `docs/prompts/milestone13_fable.md`): the pipeline works end to end, but the
furniture and the outdoor models look bad and the placement is not good. Step back and re-think the problem:
(1) furniture that looks like real products with real materials and sizes, a complete set per room; (2) outdoor that
looks real (trees, shrubs, hedges, ground, paving, walls, pools); (3) placement a designer would accept; (4) a
measurable before/after on real02, real03 and real04. Licences may be relaxed for the PoC (user position of 12 Oct
2026, §5), behind a switch and with full attribution.

Session: cloud (`CLAUDE_CODE_REMOTE=true`, no GPU), branch `Claude/Fable_01`, 12 Oct 2026. Steps 0 and 1 are CPU
only: no pod, no GPU, no change to pipeline code. This document is the result of step 0 (diagnosis, §1) and step 1
(research §2, three approaches §3, comparison §4, recommendation §5-§9).

Status: **waiting for the user's OK** (decisions in §10). Nothing of step 2 is built.

How this was made: a 60-agent workflow (3 image reviewers over all 182 committed renders, 6 diagnosis agents on
the logs and code, 6 research agents against official sources, 45 adversarial verifiers of the licence and count
claims, 3 proposal writers and 3 critics), then this write-up by the lead. Every repo number comes from a python3
script on the committed files; web facts name their source and whether it was read on the official page
(`official`) or only through a search snippet or mirror (`secondary`). The per-view review data is committed in
`results/review/m13_step0/`.

## 0. Short version

**What hurts the images most (real04, M12 code, 48 views; share of views; details §1):**

| Rank | Cause | Share of views | Mean score of those views |
|---|---|---|---|
| 1 | bare, flat materials (flat shell slots, one oak tint on every wood, plastic fabrics, parametric fixtures) | 54 % | 2.0 |
| 2 | lighting (daylight 300× too weak, rooms pushed +3..+8 EV, one invisible light per windowless room) | 52 % | 1.7 |
| 3 | cameras on bare walls (12 of 48 views are hall landings; 18 mm lenses at 1.25 m) | 44 % | 1.5 |
| 4 | empty rooms and missing anchors (43 drawn pieces not built: beds, sofas, tables, wardrobes) | 31 % / 21 % | 1.1 / 1.2 |
| 5 | lollipop vegetation and flat outdoor (100 ellipsoid "trees" from a drawn hedge, flat lawn, pool boxes, black sky) | 31 % / 21 % | 1.6 / 2.1 |
| 6 | boxy parametric pieces and odd placement (chairs on ottomans, sofas facing nothing) | 27 % / 25 % | 1.9 / 1.8 |

Mean score 1.88 of 5 (real02 1.78, real03 1.85). The only room scoring 4 is the one where every anchor is a real
product model (`r_L0_yatak_odasi`: ABO bed, wardrobe, nightstands, desk, chair). Coverage and choice of models,
light and cameras decide the score; the renderer does not.

**Root causes, ranked by image impact (details §1.2-§1.8):**

1. The fit leaves drawn anchors empty: the library has no model near the drawn size, the M12 caps refuse the rest,
   and sofas, beds and tables never fall back to a built mesh (M12 decision D14). 20 of 33 drawn anchors of real04
   are not built; 4 of 8 bedrooms have no bed; 4 of 4 living rooms have no sofa.
2. The fit picks weak models: a "recolourable wood first" re-sort overrides the ranking (one Objaverse chair of
   unknown units is used 40 times in real04 and 42 times in real02); audit quality, units, faces and texture maps
   are never ranking inputs; half of the built library pieces are stretched > 5 %.
3. Daylight is physically wrong: the sun is 3 W/m² (Blender's clear-sky reference is 1000), the interior HDRI is a
   low-contrast sunset; every daylight room is metered at +3..+8 EV and the panes are pulled dark.
4. Scene materials are flat: 72-81 % of every interior frame is shell; ceilings, worktops, fronts, ceramics, metals
   are flat colours; displacement, sheen, coat, bevel node and AO are never used; the brief's fabric colour never
   reaches a model (`complete.py` writes material tags only).
5. Placement starts from invisible obstacles: unbuilt drawn anchors and 44 untyped drawn pieces block the solver;
   drawn groups are not units; the agent then moves chairs toward a table that does not exist (24 accepted moves,
   0 effect) and 84 % of the round-1 findings survive 6 rounds.
6. Outdoor is parametric: the 101 drawn circles (r 0.36 m, in rows of 42 and 45) are read as 4 m trees, not as
   hedges; grass, paving and pools are flat; the sky has no sun disc and the world is black below the horizon.
7. Cameras: 18/16 mm lenses (90-97° field) at 1.25 m, and 12 of 48 views spent on bare landing walls.

**Recommendation (§5):** build the licence-neutral core first (anchor never empty, fit ranking, placement units,
lighting, materials, cameras, hedge/tree/site), grow the library commercially-safe (ABO by size grid, Poly Haven at
2K incl. 20 CC0 trees, ambientCG), and add HSSD (CC BY-NC 4.0, real products incl. bath and kitchen fixtures) as a
switchable relaxed layer if you accept its terms. Three full runs plus audits cost about $45-55 at the real pod
price ($2.49/h, not the $2.09 the docs quote); the project total needs a raise to about $230 for a reserve.

## 1. Diagnosis (step 0)

### 1.0 Inputs, method, and one caveat about code versions

- Renders: `results/final/<p>/*_final_preview.jpg` (real02 49 files, 41 in its report; real03 85, 83 in its
  report; real04 48 incl. 4 exterior). Building JSON: `results/furniture/<p>/building_final.json`. Agent logs:
  `results/agent/<p>/log.json` (real04 also `metrics.json`). Library: `wenart/furniture/catalog_library.json`,
  `catalog.json`, `results/library/audit/p3`, `p4`.
- **The committed real02 and real03 results are M11 runs of 10 Oct 2026** (run ids 20261010-015217 and
  20261010-153706: 15 % non-uniform cap, no audit, no group solver, grey boxes for untyped pieces). **Only real04 is
  the M12 code** (pod `jeqodk9uyn9o6p`, 11 Oct, 6 agent rounds + a final critical round, polish off). The M12 P6/P8
  runs of real02/real03 were not committed and their outputs were removed from the volume on 12 Oct. Every number
  below says which code it measures. A like-for-like before/after for real02/real03 needs one M12 baseline run (§7).
- Every count is from a python3 script over the committed files (scripts kept in the session scratchpad; the
  per-view review is committed under `results/review/m13_step0/`). Line numbers refer to HEAD `5a69ff5`.

### 1.1 What a viewer sees: every committed render, tagged

Rubric: tags from a fixed list and a score 1-5 per view (1 = embarrassing, 5 = could show a client). Tags:
`missing_anchor` (living room without sofa, bedroom without bed, dining without table, kitchen without run/sink/hob),
`empty_room`, `parametric_boxy`, `grey_box`, `floating_or_odd_placement`, `overlap_cut`, `blocked_door_window`,
`bare_material`, `wrong_scale`, `lollipop_vegetation`, `flat_outdoor`, `bad_camera`, `lighting_bad`, `decor_wrong`,
`looks_acceptable`.

| Project (code) | Views | Mean score | 1 / 2 / 3 / 4 / 5 | Top tags (views, share) |
|---|---|---|---|---|
| real04 (M12) | 48 (44 interior, 4 exterior) | 1.88 | 20 / 17 / 8 / 3 / 0 | bare_material 26 (54 %), lighting_bad 25 (52 %), bad_camera 21 (44 %), lollipop_vegetation 15 (31 %), empty_room 15 (31 %), parametric_boxy 13 (27 %), floating_or_odd 12 (25 %), missing_anchor 10 (21 %), flat_outdoor 10 (21 %), decor_wrong 7, overlap_cut 5, blocked 3, wrong_scale 2; looks_acceptable 3 |
| real02 (M11) | 49 files (41 in the report) | 1.78 (1.90 over the 41) | 15 / 30 / 4 / 0 / 0 | bare_material 28 (57 %), lighting_bad 24, bad_camera 24 (49 %), parametric_boxy 23 (47 %), floating_or_odd 18 (37 %), flat_outdoor 12, empty_room 11, decor_wrong 11, grey_box 8, lollipop 7, wrong_scale 6 |
| real03 (M11) | 85 files (83 in the report; 0 exterior) | 1.85 | 28 / 43 / 13 / 1 / 0 | grey_box 47 (55 %), bare_material 40 (47 %), bad_camera 31 (36 %), floating_or_odd 30 (35 %), parametric_boxy 27 (32 %), decor_wrong 18, empty_room 13, missing_anchor 11, blocked 10, lighting_bad 5 |

By room type, real04 (views, mean): exterior 4 / 1.0; living 3 / 1.3; hall 12 / 1.6; kitchen 3 / 1.7; bathroom
8 / 1.9; bedroom 9 / 2.0; play room 3 / 2.7; balcony 6 / 2.8. real03: bathroom 11 / 1.4, vestibule 3 / 1.0, hall
14 / 1.7, bedroom 24 / 1.9, living 24 / 2.0. The worst real04 views: the basement living room (10 drawn chairs in
rows, no table, no sofa; armchairs standing on pink ottomans), the master bedroom (a floor lamp, curtains, no bed),
the second bedroom (wardrobe parked 0.36 m in front of the window, no bed), the aerial site view (30 % black sky,
flat lawn, pool boxes), the corner exterior (a palisade of 4 m ellipsoids).

What the images say about the causes: `empty_room` and `missing_anchor` views score 1.1-1.2 and all trace to library
gaps; `bad_camera` scores 1.5 because 12 of 48 cameras were spent on bare landing walls; `bare_material` and
`lighting_bad` are the most frequent tags but score about 2, so they cap the quality rather than destroy a view. The
three acceptable views are the one bedroom where every anchor resolved to a real product model.

### 1.2 Library models and the fit (model quality, model choice)

All three projects together use 30 / 33 / 26 distinct library models for 148 / 88 / 119 built library pieces.

| Measure (built library pieces) | real02 (M11) | real03 (M11) | real04 (M12) |
|---|---|---|---|
| Pieces: library / parametric / none (not built) | 150 / 132 / 0 | 89 / 104 / 0 | 131 / 115 / 43 |
| Built: library / parametric (of which grey `unknown` boxes) | 148 / 109 (32) | 88 / 70 (42) | 119 / 58 (0) |
| Library by source: ABO / Objaverse / generated | 72 / 70 / 6 | 53 / 13 / 22 | 60 / 54 / 5 |
| Top model and its share | Objaverse "Chair" 42 (28 %) | ABO bed 8 (9 %) | Objaverse "Chair" 40 (31-34 %) |
| M12 audit vision quality ≤ 3 ("plain / game-like") | 55 % | 70 % | 52 % |
| Model units unknown (normalised to a typical footprint) | 51 % | 40 % | 50 % |
| Non-uniform stretch > 5 % | 54 % | 37 % | 46 % |
| Wood slots recoloured to one flat oak tint | 72 % | 41 % | 54 % |
| Fabric colour of the brief applied | 0 | 0 | 0 |
| Model later removed by the M12 audit | 14 % | 7 % | 0 |

How the fit chooses today (`wenart/furniture/fit.py`): usable (audit, licence) → exact style family (M12 adds a
fallback chain) → chaise side → design material tags as a hard filter → `rank_key` (generated last, known units,
real-size error in 5 % steps, judge quality, aspect error, source order) → **a re-sort that puts every model with a
recolourable wood slot in front of all others** (`fit.py:539-542`, triggered for every piece because `style.json`
names a furniture wood, `looks.py:396-397`) → caps (10 % non-uniform, mean scale 0.85-1.20, height ± 15 %). The
re-sort is why the Objaverse chair (units guessed ×0.01, 108k faces, 10 loose parts) beats the real ABO chair that
`rank_key` ranks first, and why a 1,748-face ABO nightstand beats a 20,542-face one 19 times. Replaying the fit
without the design changes the model of 44 of 119 real04 and 48 of 148 real02 built library pieces. Face count,
texture maps and the M12 audit quality are never ranking inputs (the M12 bug B1 fix only restored the M8 judge score,
which is 4-5 for every usable model).

Materials of the models: the catalogue records only whether a slot has a base-colour texture; normal, roughness and
metallic maps and texture size are recorded nowhere (`wenart/assets/recolour.py:151`). ABO models are one atlas
material (360 of 444 usable), generated models one baked colour texture, 8 of 58 Objaverse models flat colours.
The builder keeps each GLB's materials (`furniture.py:17`) and only recolours wood slots to a tint keeping 60 % of
the texture luminance (`furniture.py:1333, 1365`). The brief's "light grey fabric sofa" never arrives: the completion
stage writes `design.material_tags` only (`complete.py:725`) and the fit needs `design.fabric_colour`
(`fit.py:344-350`); so ABO sofas, ottomans and cushions keep their product colours (the pink ottomans).

The agent cannot repair a bad model: its `swap_model` pins pass the same fit rules; 19 of 21 pins on the final
real04 pieces were refused ("fails the fit rules: style, caps, look") and the crude Objaverse toilet (vision quality
2) stays in all 10 bathrooms after 44 toilet swaps.

### 1.3 Sizes, caps and library gaps

real04 (M12): 43 pieces with `asset.method: none`, all `from_documents`, in 13 of 38 rooms and 21 of 48 views:
chair 12 (0.71 × 0.45 and 0.58-0.60 × 0.45), table_dining 8 (3.35 × 1.00, 2.30 × 1.00, 0.79 × 0.65), wardrobe 4
(2.57 × 0.74, 3.11 × 0.60), floor_lamp 4 (0.79 round), table_coffee 4, bed_double 4 (2.55 × 2.00), sofa_corner 2
(4.38 × 1.97), sofa 2 (1.30 × 0.63), bookshelf 2, potted_plant 1. The rule that leaves them out:
`fit.py:437-438, 469-473, 637-649, 678-687` and `catalog.py:579-593` ("never a parametric sofa, bed or table",
M12 decision D14); the builder then refuses them (`blender/furniture.py:115, 868-878`).

| Cap setting (non-uniform, mean scale) re-run on the 43 | Still not fitted |
|---|---|
| M12: 10 %, 0.85-1.20 (committed) | 43 |
| M11: 15 %, 0.75-1.30 | 30 |
| 25 %, 0.70-1.40 | 15 |
| 50 %, 0.50-2.00 | 3 |

So 13 of the 43 are empty only because of the tighter M12 caps; 30 have no model within any sane cap because the
library has none near the drawn size: usable widths are table_dining 0.75-2.41 m (drawn 3.35 and 2.30), wardrobe
0.99-2.16 (drawn 2.57 and 3.11), sofa_corner 1.99-3.42 (drawn 4.38), chair near-square 0.43-0.74 (drawn 0.71 ×
0.45), sofa depth ≥ 0.66 (drawn 0.63). Over the three projects only 7 of 20 drawn anchor footprints (35 of 79 pieces)
have a usable model within ± 10 %, 13 (56) within ± 20 %. The library was built to 20 models per type
(`objaverse.py:223`, 188 accepted models dropped) and the survey refused 373 ABO products by a size range, so it is
thin exactly where the drawings are large.

Which drawn sizes are real: the 4.38 × 1.97 corner sofa and the 3.35 × 1.00 ten-seat table are real sizes (the
size table's own notes cite them; `size_table.yaml:73, 99`); the 2.57 and 3.11 m wardrobes are built-in runs; the
2.55 × 2.00 "bed" is the YATAK block (2.00 × 2.68 m, three pieces: bed plus nightstands); the 0.71 × 0.45 chairs
and 0.79 × 0.65 tables come from the M11 split of a "table + 2 chairs" block; the 0.51 × 0.11 sinks are a bowl
drawn twice. So about 8-12 of the 43 are real sizes the library lacks and 21-33 are doubtful readings that a
product-size snap before the fit would repair (CLAUDE.md already allows "change its size to a real product size").
Today `sizes.product_size` is used for fixtures only; `F2` (size out of range) fires only on in-scene pieces, so
the misread beds and tables never got a finding.

real02/real03 (M11, 15 % caps): 46 and 25 pieces went parametric "no candidate within caps" (washbasins 1.00 × 0.55
×10, bathtubs 1.83 × 0.80 ×8, toilets 1.15 × 0.36 ×6 misread, the same corner sofa, table and wardrobes). A CPU
re-fit with the M12 code estimates 19 and 22 `none` pieces plus 56 / 18 by-design fixture gaps for them.

Agent view of the gaps: 465 `library gap` findings in real04 (66-67 per round × 7), 0 edits possible on them
(`swap_model` is offered only for built pieces, `edit_ops.py:1270`; `report_library_gap` is record-only).

### 1.4 Placement

real04 (M12) findings per round (critical / major / minor): R1 7/159/97, R2 2/157/100, R3 2/157/98, R4 3/154/97,
R5 33/179/98 (the agent flattened the roof from a corridor session, 29 "pokes through the roof" criticals), R6
5/150/96, R7 3/146/95. Never moving: F8 "neither against a wall nor in a group" 38, G10 bathroom clearances 18,
NR untyped drawn pieces 22, LG library gaps 66, R3 door swing 10. Of the 161 unique critical/major findings of
round 1, 136 (84.5 %) are still there in round 7.

| Group completeness, real04 building_final.json (in scene = built and method ≠ none) | Value |
|---|---|
| Bedrooms with a bed in the scene | 4 of 8 (2 drawn with a model, 2 added by the solver in empty rooms) |
| Living rooms with a sofa / TV unit / coffee table in the scene | 0 / 0 / 0 of 4 |
| Drawn dining tables in the scene | 0 of 8 (36 chairs stand around nothing) |
| Kitchens with a fridge / sink / hob | 0 / 3 / 3 of 4 |
| Bathrooms with toilet + washbasin / with shower or tub | 10 / 8 of 10 |
| Nightstands at the headboard | 8 of 8 (M12 fixed the M11 defect: real02 8 of 12 wrong, real03 4 of 5) |
| Placement findings of round 7 on drawn pieces / solver-added pieces | 118 / 0 |

Where the solver fails and why (CPU re-run of `wenart/furniture/solver.py` with counters, node counts equal to the
pod's): r_L0_banyo 344 positions, 334 blocked by the free-space layer (washbasin + toilet + an untyped 1.83 × 0.80
piece that is the drawn bathtub = 47 % of the floor), 10 fail the 0.53 m front zone, 0 placed; drop the untyped tub
and a shower fits. r_L0_e_yatak_odasi: 778 positions, 642 blocked (the invisible 2.55 m bed and 3.11 m wardrobe
and their reserved zones), 0 placed; drop them and the solver places bed + 2 nightstands + wardrobe + desk + chair
(score 38.9). r_L-1_salon: 11,080 positions, 0 placed (invisible table and sofa plus 10 fixed chairs); with the
drawn group freed it places sofa + TV unit + coffee table + dining + chairs + bookshelf. r_L-1_mutfak: the fridge
candidate exists but the NKBA hard rules refuse it (work triangle 3.38 m > 2.70, landing 0.00 < 0.38). Relaxing
the minimums alone places nothing in the three blocked small rooms; removing the invisible obstacles does. So:
invisible drawn pieces are the blocker in 4 of 6 cases, hard kitchen rules in 1, a program error (an entrance group
in a stair landing the stair fills 100 %) in 1.

Other placement facts: drawn pieces are immovable for the solver (`solver.py:1780-1796`) and the agent may move one
0.3 m (41 `drawn_lock` rejections); the seating group exists only for room type `living`, so the 40 m² play room
with two drawn sofas gets "no completion" and its sofas are flagged wrong-type; 16 of 17 S2 "cuts a wall" findings
are 1.2-2.5 cm (tolerance 1.0 cm), chased with 39 accepted edits; F8 blames the chair, never the missing table.

M11 → M12 on the same villa (real02 M11 vs real04 M12, major findings): F3 back not on a wall 18 → 7, F4 facing
26 → 4, F9 overlap/box 50 → 13, F1 wrong type 9 → 1; F8 5 → 38 (the M12 rule names partners, which are unbuilt);
grey boxes 32 → 0 but unbuilt anchors 0 → 40. M12 traded white boxes for missing anchors.

### 1.5 The agent loop

real04: 183 accepted / 171 rejected edits, 981 model calls, 64 agent minutes = 56 % of the 114-min pod ($2.66);
49 % of the loop time is re-building and re-rendering previews after edits that change nothing visible.

| Fact | Number |
|---|---|
| Accepted edits whose finding was gone next round (matched by check and target) | 20 of 160 |
| Accepted edits with the plausibility score unchanged | 139 of 183 |
| `swap_model` (35 % of accepted) | 64, of which 40 toilet swaps among three generated models for 1.2-1.3 cm wall cuts; no visible change |
| `move_piece` for F8 (chair toward an unbuilt table) | 24 accepted, 0 effect |
| `relayout_room` | 8 accepted = the same candidate re-applied on two rooms, score 60 ↔ 54 |
| `place_group` | 6 accepted, each placed a duplicate washbasin instead of the shower (`edit_ops.py:768-769` builds the program entry without the drawn members); removed again 5× |
| `complete_group` / `fix_fixture` / `move_group` | 0/18, 0/19, 0/3 (offered although the dry run fails or the piece is locked) |
| `set_exterior` roof | set 10 times in 6 rounds from 6 room sessions (flat / mansard / gable); last writer wins; round 5 collapsed |
| `set_camera` | 1 of 11 (the model sends z = 1.6 absolute on a sloped site) |
| Rejections: drawn_lock / memory repeat / max_tries / fixture_place | 41 / 31 / 27 / 13 (65 % of all rejections aim at locked, unbuilt or impossible targets) |
| Vision critic | 83 calls, 50 kept findings, 18 accepted edits (13 of them toilet/sofa swaps with no visible change); real hits (no bed, floating wardrobe, crude toilet) have no tool |
| Of the 146 final critical/major findings, reachable with any current tool | about 35 (24 %) |

Root causes: acceptance measures "score did not drop", not "finding gone" (`edit_ops.py:1179-1196`); findings are
mapped to tools by check id, not by cause (`brief.py:55-105`); every room session gets every room tool and the
building tools (`tools.py:209-211`, `loop.py:149-154`); the library gap, the only visible problem, has no tool;
`retype_piece` changes the type but leaves `build: false` and the needs-review entry; the critic is told "4 levels"
because the variant counts as a level. The M12 bake-off already showed no open model judges layouts from top-down
images; this log shows the loop also cannot fix what the fit and the reader left behind.

### 1.6 Materials, lighting and the render look

| Fact | real02 (M11) | real03 (M11) | real04 (M12) |
|---|---|---|---|
| Interior views at EV ≥ +5 / ≥ +3 / at the +8 limit | 9 / 12 / 3 of 35 | 27 / 59 / 8 of 83 | 9 / 12 / 0 of 44 |
| Daylight-only rooms: EV median; metered incident p50 | +6.75; 0.008 | +4.83; 0.031 | +6.50; 0.011 |
| Rooms lit by the assumed invisible ceiling light: EV median; p50 | −0.50; 1.28 | −0.50; 1.27 | −0.67; 1.43 |
| Views with the window pull (1-4 stops) | 11 | 42 | 11 |
| Interior views lit by the assumed light alone | 66 % | 30 % | 73 % |
| Furniture share of the frame; parametric share of furniture pixels | 27 %; 54 % | 29 %; 50 % | 19 %; 44 % |
| Distinct CC0 texture sets in the scene | 9 | 5 | 9 |
| Samples; seconds per view (OptiX, OIDN) | 128; 3.3 | 128; 4.7 | 128; 3.3 |
| Polished final views | 0 of 41 | 0 of 83 | 0 of 48 |

100 % of the 45 views at EV ≥ +5 are daylight-only rooms: the sun lamp is 3.0 W/m² (`lighting.py:362`; the Blender
5.2 manual's clear-sky reference is 1000 W/m²), the interior world is the Poly Haven HDRI `kloppenheim_06` (tagged
sunset, partly cloudy, low contrast) at strength 1.0, and a room with a window gets no fill light by rule
(`lighting.py:8-11`), while a windowless room gets 12 W/m² of floor from one invisible square light at the pole of
inaccessibility. Lamps, pendants and ceiling lights never emit in the daylight mood (`furniture.py:459-465`). The
exterior sky has no sun disc at strength 0.5 (`materials.py:927-966`); per-view auto white balance spans
4,900-10,000 K; the +6..+8 EV pushes show denoiser smearing (OIDN already runs at Accurate / High, the defaults).

Shell materials (72-81 % of every interior frame): ceiling flat `plaster_white`, worktop flat grey `stone_worktop`
(roughness 0.3), fronts and trim flat `painted_wood_white`, sanitary flat `ceramic_white`, handles flat
`steel_brushed`, wet rooms a procedural 60 × 30 grid with 2 mm grout, walls a plaster photo in "flat" mode
(luminance only), fabrics the linen photo in flat mode; displacement is never connected (`materials.py:7-8`);
no sheen, coat, bevel node, AO node or imperfection map anywhere in `wenart/blender` (grep: 0). Parametric pieces
get 2-8 mm geometric bevels, library pieces none. 46 % of the interior views show no decor item at all.

### 1.7 Outdoor and site (real04 M12; real02 M11 exteriors)

| Element | Drawn | Built today | Where |
|---|---|---|---|
| Trees | 101 circles, all r = 0.359 m, in 4 chains (42, 45, 7, 7 at 0.56-0.80 m pitch), 60 within 2 m of the plot edge | 100 trees: 8-gon trunk r 0.12 m, 10 × 6 ellipsoid crown 0.72 × 2.4 m, height = max(4.0, 1.6 × crown) = 4.0 m, flat foliage and bark colours | `sheets/exterior.py:488-498`, `site.py:67, 625-676`, `shell.py:2676-2678` |
| Hedge | not a concept of the reader; the 42- and 45-circle rows are hedges to any designer | a box hedge exists only for an inferred plot boundary (`site.py:687, 1046-1050`), suppressed when the plot is drawn | `site.py:1189` |
| Ground | 16 level marks, −6 to +3 m across 30 × 39 m (slope up to 1:0.3) | one draped TIN, grass photo tile 1.4 m, roughness ≥ 0.85, no displacement, no retaining walls, kerbs or steps; terraces and parking tilt with the slope | `site.py:374-428, 1463-1477` |
| Pools | 4 × 24 m² | basins whose edge is the highest corner: 1.2-2.2 m of light-blue box stand out of the downhill ground; no coping, no deck; flat water plane | `site.py:1234-1275` |
| Sky, sun | north unknown | physical sky, no sun disc, strength 0.5; per-view WB up to 10,000 K; black below the horizon (the skirt of 972e65b was committed after the run and by geometry still leaves ~9 % black in ext_7) | `materials.py:924-971` |
| Facade | no elevations drawn | flat greige plaster in flat-albedo mode, white slab bands, no reveals, gutters, canopy, lights, railings | `facade.py`, `exterior.py:75-79` |
| Cameras | 7 planned | 4 rendered: ext_3/ext_4 dropped (63-87 % blocked by the tree palisade), ext_6 inside the copy b2; the site view's own check failed and was kept | `exterior.py:545-569, 852-860` |

Frame shares (HSV classifier): ext_1 sky 40 %, lollipops 20 %, lawn 6 %; ext_7 black 30 %, lawn 25 %. real02
(M11): 2 inferred 5.6 m spheres and a flat green box hedge in all 6 exterior views. The agent never mentioned trees,
hedges, pools or the sky in 2,924 events; no checklist item judges vegetation.

### 1.8 Plain bugs and small facts found (not fixed; step 0 is report only)

| # | Bug | Where |
|---|---|---|
| B1 | fabric colour never reaches the fit (`design.material_tags` only) | `complete.py:701-729`, `fit.py:344-350` |
| B2 | `retype_piece` keeps `build: false`, status unverified and the needs-review entry | `edit_ops.py:456-497` vs `critic_code.py:160` |
| B3 | `place_group` builds the program entry without the drawn members → duplicate washbasin | `edit_ops.py:768-769`, `solver.py:1482-1500` |
| B4 | `set_exterior` has no id, so its max-tries key is shared by 23 parallel sessions; room sessions may set the roof | `tools.py:816-824`, `brief.py:466-467` |
| B5 | the vision critic is told `len(levels)` = 4 (the variant counts) → "4 levels but 2-storey" critical for 5 rounds | `critic_vision.py:179-180` |
| B6 | F2 (size outside the product range) runs on in-scene pieces only, so misread unbuilt anchors never get a finding | `plausibility.py:166-169` |
| B7 | `sizes.product_size` is used for fixtures only; furniture keeps misread sizes | `sizes.py:237-261`, no call in `fit.py` |
| B8 | the 0.8 m `tree_min_height` turns a 0.36 m shrub symbol into a 4 m tree | `site.py:67, 656-676` |
| B9 | the site-view camera (24 mm, 28° down, 21 m up) has its frame top 5° below the horizon: black band by construction | `copies.py:22-23, 49-76` |
| B10 | 12 of 48 real04 cameras on landing walls: halls get up to 3 views regardless of content | `camsearch.py`, area rule |
| B11 | the two L0 entrance doors are drawn twice 0.16 m apart (d_L0_005/013, d_L0_006/014): two frames and handles in one opening | `building_final.json` openings |
| B12 | bathroom mirrors and art hung so high the ceiling or roof cuts them (6 of 8 bathroom views) | decor height rule (`rest.py`) to check |
| B13 | the M12 audit record has no PBR map or texture-size fields; `thumbnails.json` images median 2-3 | `audit/glbmesh.py:200-207`, `recolour.py:151` |

## 2. Research (step 1): what exists, what it costs in licence terms, what was verified

Method: six research agents searched widely (WebSearch) and read the official pages the session proxy allows
(huggingface.co, github.com and raw files, api.polyhaven.com, ambientcg.com, docs.blender.org); 45 verifier agents
then tried to refute every decisive claim of every candidate from the official source. "Verified" below means the
licence text or the count was read on the official page or file; "secondary" means a search snippet or a mirror
(the official page is blocked here: tianchi.aliyun.com, terms.aliyun.com, sketchfab.com, blenderkit.com, fab.com,
extensions.blender.org, nkba.org, arxiv.org). Blocked URLs are listed per area in the agents' notes.

### 2.1 Furniture and decor sources

| Source | Licence (decisive clause) | Commercial | What it holds for us | Access, size | Verified | Verdict |
|---|---|---|---|---|---|---|
| **HSSD** `hssd/hssd-models` | CC BY-NC 4.0 ("You agree to use this dataset under the CC BY-NC 4.0 license terms"); gated (auto) | **no** | real products (Floorplanner) in metres, PBR GLB; mirror csv 17,503 rows: sofa 393 + L-shaped 61, armchair 351, bed 386, dining table 288, coffee table 205, nightstand 202, wardrobe/armoire 169, chest of drawers 274, bookcase 243, tv stand 91, rug 775, throw pillow 498, wall art 1,286, potted plant 357, **toilet 51, sink 109, bathtub 96, shower 62, fridge 58, stove 50, kitchen cabinets 288, kitchen island 59**; 2,108 articulated | HF, user must accept the terms with the account behind the pod's token; 38.45 GB, 14,270 files; polycount and texture size not stated | official (card, API); counts from a public mirror csv | the only source with real bath and kitchen fixtures; relaxed mode only |
| 3D-FUTURE / 3D-FRONT (Alibaba) | Tianchi research agreement 2020: scientific research only, no redistribution, no commercial use of results | **no**, not even derived statistics | 9,992-16,563 designer models; 18,968 rooms as a layout prior | Tianchi login (blocked); HF mirrors are unauthorised copies | secondary (licence page blocked) | not recommended |
| **ABO 3D models** (remainder) | CC BY 4.0 (README: "licensed under the Creative Commons Attribution 4.0 International Public License"; credit "Amazon.com"); the 2021 paper said CC BY-NC, the live index says CC BY | yes (attribution) | 7,953 GLBs, mean 20.8 MB, 53 % 4K / 47 % 2K textures, mostly one material slot; 4,708 mapped furniture listings never judged (sofa 859, chair 1,184, table 584, bed 140 + 52 frames, headboard 206, rug 817, wall art 599, pillow 275, planter 182); catalogue photos (398,212) under the same licence | public S3, scripted (`wenart/assets/abo.py`) | official (README, csv, tar listing) | grow by size grid, not by count |
| **Poly Haven models** | CC0; API ToS: free for any purpose incl. commercial since 18 Jul 2026 (commit history), unique User-Agent required, "Powered by Poly Haven" credit for live-API apps | yes | 521 models (12 Oct 2026): furniture 85 (12 modern, 58 vintage), lighting 29, **trees 20 (7 full canopy), plants 57, ground cover 32, grass clumps 4, potted plants 6**, planters; polycount in the API (jacaranda 312k, island_tree_01 3.7 M, pine_tree_01 17.4 M); no wardrobe, bed_double, tv_unit, kitchen or sanitary models | API, bulk allowed; 20 trees at 2K glTF = 2.66 GB; we fetch 1K only today (`furniture.py:251`) | official | use at 2K; trees and plants now |
| **ambientCG** | CC0 (homepage: "free to use without attribution - even in commercial circumstances") | yes | 2,015 materials: Fabric 89, Leather 50, Wood 102, Metal 101, PavingStones 155, Tiles 164 (14 tagged pool), Ground 128, Gravel 44, Bark 15, Carpet 16, imperfection overlays 34; displacement maps on 1,985, AO on 1,195; 39 leaf/foliage atlases (18 are older "PBRApproximated" sets); 34 3D models (food, a stump) | API v2; downloads redirect to `acg-download.struffelproductions.com` (on the allow-list); 39 atlases at 2K PNG = 1.44 GB | official | use for shell, fabrics, paving, pool tiles, leaf cards |
| TexVerse | ODC-By (dataset) + per object: CC BY 699,075, CC0 6,139, NC/SA/ND 153,455 (uploader-declared) | conditional (82 % CC BY/CC0) | 858,669 Sketchfab models with ≥ 1K textures, 158,518 PBR (19k spec/gloss); furniture counts unknown until `metadata.json` (837 MB) is read on the pod; 4K/8K natives have no 2K file (1K 12.6 MB, 2K 13.8, 4K 31.9, 8K 48.7 MB); the authors' own quality funnel keeps ~31 % | HF, not gated; the LFS CDN is blocked here, reachable from the pod | official | optional, later; count per type first |
| Objaverse++ | ODC-By (annotations) | yes (filter only) | 789,195 rows: quality score 0-3, style flags ("experimental", not in the paper) | 0.24 GB | official | pre-filter only; covers ≤ 40 % of TexVerse |
| OmniObject3D | CC BY 4.0 (README) | yes | 6,000 scanned objects, 190 categories; furniture classes unverified; access via OpenXLab login (no official HF repo) | 13 GB textured mirror | official (licence), categories unverified | optional for scanned decor |
| Google Scanned Objects | CC BY 4.0 per object | yes | 1,030 household objects, ≈ 0 furniture (done in M12: 36) | HF mirror | official | done |
| Pix3D, PhotoShape, ShapeNet, PartNet, IKEA sets, Replica, Matterport | untextured / NC / research / academic | no | – | – | official | not usable |
| Meta DTC | CC BY-SA + no-sale clause | conditional (SA) | 2,000-2,400 scans, 4K PBR | projectaria (blocked) | secondary | no |
| BlenderKit | per asset RF or CC0; terms unread (site blocked; 2018 terms "addon only") | conditional | 81,687+ models, ~22,000 free; furniture count unknown; a REST API exists (BlenderProc uses it keyless for free assets) | API key; legal status of scripted bulk use unclear | secondary | not in M13; read the terms from the Mac first |
| Sketchfab live | per upload; download API needs per-user OAuth, "contact us" for unattended use | conditional | same pool as Objaverse/TexVerse | blocked | secondary | use Objaverse/TexVerse instead |
| Fab / Quixel Megascans | Fab Standard licence; Megascans paid per asset since 2025; no API | conditional | top scans | manual only | secondary | no |
| TurboSquid, CGTrader, 3D Warehouse, IKEA web | scraping and bulk download forbidden / no licence | – | – | – | secondary | no |
| Dimensiva, Chaos Cosmos, BIM portals | manual / V-Ray only / manufacturer terms | – | – | – | secondary | no |
| Kenney, Quaternius | CC0 | yes | low-poly | – | secondary | no (not photoreal) |

Findings: every large designer-furniture dataset is non-commercial (HSSD, 3D-FUTURE/3D-FRONT, ShapeNet, IKEA,
Replica). **No open, commercial-safe library has realistic bath or kitchen fixtures** (toilets, basins, tubs,
showers, fridges, stoves): ABO has none, Poly Haven has none, Infinigen's fixture factories mostly failed our own
M12 audit (§2.3). HSSD is the one source that has them with real products. ABO is the only commercial-safe source
with real sizes and PBR glTF at scale; its "simple" look comes from budget product brands with one material slot and
from our own flat recolour, not from the maps (53 % are 4K).

### 2.2 Vegetation and outdoor

| Option | Licence | Commercial | What it gives | Headless on the pod, Blender 5.2 | Verified | Verdict |
|---|---|---|---|---|---|---|
| **Poly Haven trees, plants, ground cover** | CC0 | yes | 7 full-canopy trees (island_tree_01-03 5.0/3.4/2.6 m, tree_small_02, jacaranda, pine_tree_01, fir_tree_01), 4 shrubs, 3 grass clumps, 57 plants, 32 ground covers; **no palm, cypress, olive, plane, citrus, hedge**; 0.3-17 M polygons each (instances and LOD needed) | glTF/.blend import; polycount in the API | official | hero trees near cameras, grass clumps, planters |
| **Sapling Tree Gen** (Blender add-on / extension) | GPL-2.0-or-later (code only; the output mesh is ours) | yes | trunk and branch skeletons, 9 presets, 4 leaf shapes, no textures; **verified by a CPU test in the official bpy 5.2.2 wheel: generation works headless for 0.3.5 and 0.3.7, only the wind animation fails**; a meshed tree is ~150k polygons (Skin modifier) | `bpy.ops.curve.tree_add` | official (code), tested | species-look trees at drawn sizes, run as the installed add-on, not forked into the repo |
| **Infinigen nature** (princeton-vl/infinigen v1.19.0) | BSD-3 core; `infinigen_gpl` is GPL-3.0 and imported transitively (`assets/materials/__init__.py:8` plus lichen, particles, corals, seaweed, terrain); v2.0.0a3 (8 Oct 2026) makes the import optional | yes for the core (the pod already runs it in its own bpy 4.2 / Python 3.11 venv, flagged in `docs/plan.md`, user OK 11 Oct) | 7 tree config families (basic, palm, baobab, bamboo, shrub, pine, space), 5 leaf shapes, grass/leaf/rock scatters; "weird units" (scale 0.35), per-tree time unpublished, OBJ export of whole trees unsupported (hand over as .blend) | second venv (bpy 4.2.0 wheel 519 MB) | official | second generator, after a timing test |
| ambientCG leaf/foliage atlases, bark, paving, pool tiles, ground, imperfections | CC0 | yes | 39 atlases (opacity maps; 10 with scattering), Bark 15, PavingStones 155, pool Tiles 14, Ground 128, Gravel 44 | textures | official | leaf cards for hedges and crowns, surfaces |
| Poly Haven textures and HDRIs | CC0 | yes | bark 24 (platanus, palm, pine), grass 22, cobblestone 38; 997 HDRIs: 299 skies, 59 tagged pure sky, 301 indoor; up to 16K | textures | official | sky and ground |
| Own geometry-nodes hedge, grass, leaf-card crowns | ours + Blender 5.2 nodes (Distribute Points on Faces, Instance on Points, Principled Thin Wall) | yes | a hedge from the drawn line, grass near cameras, crowns on Sapling trunks; a 20 m hedge at 400 cards/m² ≈ 14k cards | bpy | official (manual) | build |
| Blender 5.2 water: transmission + ripple normal / Ocean modifier + Volume Absorption; refractive caustics off; shadow caustics (MNEE) optional | GPL tool | yes | pool water, coping ring, clipped basin | bpy | official (manual) | build |
| Megascans/Fab plants | Fab Standard, paid, no API | conditional | top photoscans | manual | secondary | no |
| Maxtree Mediterranean packs (cypress, stone pine, palm, olive) | royalty-free, paid ($7-259), text unread | conditional | the only ready named-species source | manual | secondary | user decision; not needed for the PoC |
| Botaniq, Tree Vegetation, Geo-Scatter, The Grove, SpeedTree | paid / interactive | conditional | – | – | secondary | no |
| MTree, Arbaro, ngPlant, TreeIt | GPL / dormant / Windows | – | weak | – | secondary | no |
| Objaverse / TexVerse plants | per object | conditional | counts not obtainable here (CDN blocked); M12 judges rejected most Objaverse plants | pod | partial | no |

Findings: no CC0 source has a palm, cypress, olive or plane tree or a hedge model; species therefore stay an
"inferred look" (named in the report) built from Sapling presets, CC0 bark and CC0 leaf atlases, with Poly Haven
hero trees near the cameras. Everything vegetation is CPU work; the GPU cost is render memory and time (to measure
once). Two corrections from the verifiers that matter for the build: a **World volume disables the sun and the sky
surface** in Cycles (the manual: use a large closed mesh with a Volume Scatter material for haze), and OIDN already
runs with Accurate prefilter and High quality by default in 5.2, so the "smeared +8 EV rooms" need more samples and
real light, not a denoiser setting.

### 2.3 Generative 3D and materials (open weights)

| Option | Licence | Commercial in the EU | Input → output | Furniture quality evidence | VRAM / time | Size condition | Verified | Verdict |
|---|---|---|---|---|---|---|---|---|
| TRELLIS.2-4B (in use) | MIT weights and code; DINOv3 encoder gated custom licence (commercial allowed, trade-control clause); **the GLB export `o_voxel.postprocess.to_glb` and the texturing pipeline import nvdiffrast ("Nvidia Source Code License (1-Way Commercial)", §3.3 non-commercial research/evaluation only)** | weights yes; the export path no: **all 281 of our generated models were baked through nvdiffrast** | 1 image → PBR GLB (base colour + metal/rough, no normal map) | trained on renders (ABO + HSSD among others); our audit: 49 of 281 at quality 2, 83 % of usable generated models at ≤ 3; inputs were Z-Image renders with props | 19-42 GiB; repo median 46 s | no (unit cube) | official | keep for fixtures; flag `tool_nc`; a nvdiffrast-free bake is R&D (ComfyUI PR #14718, merged 22 Aug 2026, re-implemented the post-processing in PyTorch/SciPy, but ComfyUI is GPL-3) |
| TRELLIS.2 texturing (mesh + image → PBR on a given mesh) | same (nvdiffrast) | same | re-texture ABO/Objaverse models from their product photo | paper claims only | ~7 s material stage | keeps mesh | official | later, after a clean bake |
| Pixal3D (TencentARC, 2026) | MIT, but `extra_gated_eu_disallowed: true` on HF; TRELLIS.2 backbone | **no (EU flag)** | image / multi-view → GLB | geometry only in the paper | ~18 GB | no | official | no |
| Hunyuan3D 2.1 / Omni | Tencent Community: "DOES NOT APPLY IN THE EUROPEAN UNION, UNITED KINGDOM AND SOUTH KOREA"; §5(c) outputs may not be used outside the Territory | **no** | Omni: image + bbox → shape (the only size-conditioned open model) | – | 10-29 GB | Omni: yes | official | no |
| SAM 3D Objects (Meta) | SAM License, gated manual with Meta privacy consent; §8 terms changeable | yes (terms) | photo + mask → mesh with vertex colour or Gaussians; layout affine-invariant (not metric); bake = xatlas UV + 1024² base colour, roughness 1.0 | real-photo model (5:1 preference on real objects, own paper) | 32 GB; ~31 s/object | pose only | official | optional spike on ABO photos; not core |
| PartCrafter | MIT (its RMBG-1.4 is NC → BiRefNet MIT) | yes | image → N untextured parts | ABO/Objaverse examples | 8 GB | parts | official | fallback for modular sofas |
| Step1X-3D, TripoSG, Direct3D-S2, Hi3DGen | Apache / MIT | yes | geometry (+ RGB) | beaten by TRELLIS.2 (own papers) | 8-29 GB | no | official | no |
| Material Anything | MIT code; base model `stable-diffusion-2-inpainting` (OpenRAIL++-M), own weights unstated; Blender 3.2 scripts | conditional | mesh → albedo/rough/metal/bump | no furniture shown | unknown | keeps mesh | official | not now |
| MV-Adapter | Apache-2.0 | yes | image + geometry → 6 views / texture | cartoon example | 14-16 GB | keeps mesh | official | no |
| MatSynth | CC0 + CC-BY mixed, 440 GB | conditional | 4,069 4K materials (from ambientCG/Poly Haven) | CPU | – | official | no (ambientCG direct) |
| Z-Image-Turbo (in use) / Qwen-Image-2512 / FLUX.2 klein 4B | Apache-2.0 | yes | text → product photo | – | 20.5 GB resident (not 13) | – | official | keep |
| Qwen-Image-2.1, FLUX.2 klein 9B, SUPIR | research / NC | **no** | – | – | – | – | official | no |

Findings: why TRELLIS.2 looks blobby here is explained by the facts: no normal map, colour per voxel (the 2048 px
bake is ~1024 real samples along the long axis), remesh and decimation to 200k faces, inputs with props, no size
condition (19 generated bathtubs 0.80 m high). Real product photos (ABO, CC BY 4.0) are a better input than
Z-Image renders. No commercial-safe generator takes a size or bounding box; long pieces must be assembled from
modules (straight sofa + chaise, table modules) or built by code.

### 2.4 Placement: data, methods, judging, rules

| Option | Licence | Usable | What it gives | Verified | Verdict |
|---|---|---|---|---|---|
| 3D-FRONT (layout prior) | research only; "derivatives or results" clause | **no**, not even statistics | 18,968 professional rooms | secondary | no |
| HSSD scenes, Structured3D, InteriorNet, RPLAN, CubiCasa5K, InteriorGS | NC / unread / unknown / NC / NC-tagged | no / unknown | human-authored layouts | official / secondary | no; InteriorGS terms to watch |
| ProcTHOR-10K | Apache-2.0 | yes | 10,000 rule-sampled houses; asset-group JSON (television-sofa, chair-diningtable-N, desk-with-chair) | official | test data and the group format (already used in M12) |
| **Permissive professional layout dataset** | – | – | **none found** | – | priors must be rules, not data |
| Holodeck | Apache-2.0 (needs GPT-4o, Unity, rtree/scipy) | ideas | constraint vocabulary (edge/middle, in front of, side of, face to, aligned, near/far) + DFS solver; humans preferred it over ProcTHOR 64 % | official | vocabulary already in `groups.yaml` (around, facing same, align) |
| LayoutVLM | no LICENSE file | ideas | VLM writes relations on a marked top-down (coordinate points every 2 m, ids, front arrows), differentiable refinement | official | marks idea for candidate images |
| Infinigen Indoors solver | BSD-3, bpy 4.2 only | ideas | hard/soft constraints, annealing | official | ideas (done in M12) |
| SceneEval | MIT (its scene builder pins bpy 4.2.13) | metrics | collision/clearance metrics; VLM-vs-human agreement: GPT-4o 84-95 %, Qwen2.5-VL-7B 77-91 % | official | metric ideas |
| SceneCritic / LEGO-Eval (2026) | – | evidence | free VLM judges agree with humans 59 % / 47 % vs 94 % / 83 % for symbolic (code) evaluators; the same scene scores 75 % or 55 % depending on the camera; tool-grounded judging F1 0.81 vs 0.40 | secondary / official | **code decides layouts; the VLM gets marked images and a narrow choice** |
| Agentic Designer, Function2Scene, SceneMosaic (2026) | unknown | ideas | propose-check-repair per piece with code checks: violation rate 17 % vs > 90 % one-shot; 94 % preference | official (abstracts) | the loop we have, with designer criteria added |
| ATISS, DiffuScene, MiDiffusion, PhyScene, ReSpace | NC weights, 3D-FRONT data | no | learned layouts | official | no |
| Open VLMs with published layout-judging results | Qwen2.5-VL-7B/32B, InternVL3.5-30B only; none for Qwen3-VL / Qwen3.8 / GLM / Kimi / Molmo (Molmo2 is Apache but trained on NC data per its card) | – | – | official | keep Qwen3.8-27B for typing and render checks; no judging of top-downs |
| NKBA kitchen/bath guidelines (4th ed.; 5th ed. May 2026) | copyright | numbers | walkway 0.91 m, behind diners 0.91/1.12 m, triangle, landings (already in `groups.yaml`) | secondary (nkba.org blocked) | keep as data |
| Turkish Planlı Alanlar İmar Yönetmeliği minimums | law | numbers | living 12 m² / 3.00 m, bedroom 9 m² / 2.50 m, kitchen 3.30 m² / 1.50 m (snippets; mevzuat.gov.tr blocked) | secondary | explains why our 0.60 m bed-side and 1.50 m TV rules fail small rooms |
| Design-book rules (Neufert, Panero & Zelnik, Ching, Time-Saver) | books | numbers | conversation circle 2.4-3.0 m, coffee table 0.30-0.45 m from seats, bed sides 0.60-0.90 m, rug "front legs on", dining 0.60 m per cover | secondary (compilations on GitHub) | score terms, flagged as secondary |

Reusable designer rules for the solver (sources flagged secondary unless noted): R1 main path 0.91 (min 0.80);
R2 secondary paths 0.75 (min 0.60); R3 conversation circle 2.4-3.0 m, seats face the centre within 45°; R4 coffee
table 0.30-0.45 m from every seat it serves, long axis parallel to the sofa; R5 sofa on the TV axis within 0.30 m,
1.2-1.6 × diagonal; R6 rug under the group (all front legs on; dining rug ≥ table + 0.60 m per side); R7 bed head
on a wall, not under a window, 0.60-0.90 m sides (0.46 absolute on one side in a 2.50 m room); R8 dining 0.60 m
per cover, 0.81 m behind a chair; R9 desk with the window beside it; R10 kitchen (NKBA, already data); R11 storage
fronts 0.80 m; R12 nothing floating (every piece on a wall, in a group or anchored); R13 alignment and mirrored
pairs, wall pieces centred on their span; R14 room-size variants below 12 m² living / 10 m² bedroom; R15 one anchor
per group.

Three placement architectures for our constraints: **A** extend the M12 solver with the designer terms and the
seven fixes of §1.4, VLM only ranks marked candidates (1-2 weeks CPU, low risk); **B** relation program written by
the VLM in a fixed vocabulary + scipy refinement (LayoutVLM re-implemented; 2-4 weeks, medium risk, 27B program
quality unmeasured); **C** a small fine-tuned proposer on our own generated rooms (4-6 weeks, high risk, no
professional ground truth). A first; it also builds the regression set B would need.

### 2.5 Render realism levers (Blender 5.2 LTS, all GPL tool / output ours; verified on docs.blender.org and the 5.2 source)

| Lever | State today | Cost | Verdict |
|---|---|---|---|
| Sun strength in W/m² (manual: clear sky 1000, cloudy 500, overcast 200) | 3.0 (`lighting.py:362`) | none | fix first; re-meter |
| Sky Texture "Multiple Scattering" with Sun Disc, Sun Intensity, Elevation; aerosols for haze | sun disc off, strength 0.5 | none | use for exteriors and daylight interiors |
| Daytime HDRIs (Poly Haven 299 skies, 301 indoor) | 1 sunset HDRI | downloads | variety per project |
| Light portals | in use | – | keep |
| Samples 256-512, adaptive threshold, filter glossy | 128 spp, 3.3 s/view | ×2-4 render time (fine) | do |
| OIDN Accurate / High | already the 5.2 default | – | nothing to do |
| Light tree | default on | – | nothing to do |
| Path guiding | CPU only | – | no |
| Displacement + adaptive subdivision (ambientCG maps already downloaded) | never connected | memory, ~1.5-2× on exteriors | ground, paving, tiles, plaster |
| Bevel shader node (2-5 mm) | geometric bevel on parametric parts only | ~+20 % | library meshes and shell edges |
| AO node (dirt, corners) | none | "expensive" (manual) | shell corners, under furniture |
| Principled Sheen (fabrics), Coat (varnish, lacquer, glazed tiles), imperfection roughness overlays | none | none | textiles, wood, tiles, metals |
| Haze: a large closed mesh with Volume Scatter (not a World volume, which disables sun and sky) | none | render time | exteriors |
| IES profiles for lamps | none; free IES sources unverified | – | optional, spot lights as fallback |
| Camera: 24 mm default (28 in large rooms), eye 1.30-1.45 m, horizon ~42 %, foreground term; hall camera budget | 18/16 mm, 1.25 m, 3 views per hall | none | do; changes the framing of "same views" (§7) |
| AI polish: Z-Image Tile ControlNet 2.1 (Apache), phase-preserving noise (Apache example code), SeedVR2 (Apache) / Real-ESRGAN (BSD) upscale | polish off; 0 of 172 committed finals polished | GPU | after the Cycles fixes; stays off in M13 unless asked |
| FLUX.2 klein 9B, SUPIR, Qwen-Image-2.1 | – | – | NC: no |

### 2.6 What the verifiers refuted or corrected (the decisive ones)

- Poly Haven: commercial API use is allowed only since 18 Jul 2026 and the ToS can change without notice; the
  assets are CC0 regardless, so download once to the volume and keep the User-Agent.
- ambientCG: 2K PNG atlases are 1.44 GB (not ~1 GB); 14 pool tiles (not 9); 18 of the 39 vegetation atlases are
  old single-photo sets; no USD; downloads go through `acg-download.struffelproductions.com`.
- ABO: only 53 % of the models have 4K textures; the licence conflict (paper NC vs README BY) is real and must be
  recorded in `docs/plan.md`; trademarks in textures are not licensed.
- TexVerse: the resolution ladder is native + 1K (no 2K for 4K/8K natives); 19k PBR models use spec/gloss;
  Objaverse++ labels reach at most ~40 % of it; style labels are experimental.
- Infinigen: the GPL submodule is imported in more places than one; the M12 P4 audit kept 15 of 27 Infinigen
  models (bathtub 3, washbasin 3, decor 9; toilets 2 "fix"), **0 of 3 kitchen sinks, 0 of 3 ovens, 0 of 3 fridges**
  (wrong size 97 % off, lying on its side, open doors, quality 2). Infinigen fixtures are not a plan for kitchens
  until those exports are fixed.
- Sapling: a fork inside this MIT-documented repo would be GPL code in the repo; the add-on works unmodified in
  bpy 5.2.2, so it is run as installed, like Blender itself.
- TRELLIS.2: the nvdiffrast dependency sits in the export of every existing generated model, not only in new ones.
- Hunyuan3D: the territorial clause also covers outputs (§5(c)); Pixal3D carries the same EU flag.
- SAM 3D Objects: gated with a manual approval and Meta privacy consent; outputs are not metric.
- Molmo2 is Apache-2.0 but its card says it is trained on NC research data; not used.
- Cycles: a World volume blacks out the sky surface and the sun; haze needs a closed mesh volume.
- GPU price: every single RTX PRO 6000 pod since 9 Oct ran at $2.46-2.60/h (median $2.49), not the $2.09 quoted
  in `docs/plan.md` and `CLAUDE.md`; RTX 5090 $1.18/h (32 GB: cannot host the 52 GB agent/judge server).
- The volume is 400 GB with about 120 GB used after the 12 Oct cleanup (user, 12 Oct); older docs still say 250 GB.

## 3. Three complete approaches (library + vegetation + placement)

Three proposal agents each wrote a complete approach from a different angle; three critic agents then tried to
refute them against the research and the repo. The numbers below are after the critiques. All three agree on a
common core (§3.0); they differ in where the anchor models come from.

### 3.0 The common core (every approach needs it; licence-neutral)

| Track | What changes | Fixes (§1) |
|---|---|---|
| K1 anchor never empty | product-size snap of misread drawn sizes before the fit (block YATAK 2.55 × 2.00 → a 1.80 × 2.00 bed + nightstands; the split 0.71 × 0.45 "chairs" → 0.50 × 0.50; both already allowed by CLAUDE.md "change its size to a real product size"); a fallback ladder: library model within the caps → a modular builder with real proportions (wardrobe runs, long tables, L-sofas from a straight module and a chaise, kitchen runs) → the parametric family with a `library gap` finding; an unbuilt anchor is never an obstacle and never suppresses its group | 1.3, 1.4 |
| K2 fit and choice | remove the wood re-sort; rank by real product, known units, audit vision quality and faces as tie-breaks (not gates: decision 1a of 11 Oct stays), texture maps recorded per model; uniform scaling to the drawn width with the depth absorbed by the layout; design tags as preferences; pins skip the style filter; a diversity penalty per room and project; fabric colour from the brief | 1.2 |
| K3 placement | untyped drawn pieces typed by the identical footprint on another level or in the twin room (within 1 cm), by block name, or by the room's missing group member of that size (`inferred`, with evidence); a drawn group (table + chairs, sofa + armchairs + coffee table, bed + nightstands) is one unit that is re-solved around the drawn anchor place when its anchor is missing or misread (each member logged `adjusted_by_ai`, bounded move); room-type aliases; tiered minimums and NKBA soft in small kitchens; S2 tolerance 3 cm (fixtures) / 5 cm (soft seating); F8 names the missing anchor; F2 on every drawn piece; designer terms R3, R6, R12-R14 as data in `groups.yaml`; the rug as a group member | 1.4 |
| K4 agent loop | an edit is accepted only when its finding is gone in the dry re-check; tools offered by cause, not by check id; building-wide tools only from the building session; idempotent `set_exterior`; `retype_piece` builds the piece; `place_group` reuses the drawn group; `swap_model` never for S2 < 3 cm; 3 rounds, not 6; the vision critic only where a tool exists | 1.5 |
| K5 light, materials, cameras | sun in the hundreds of W/m² (calibrated on 8 fixed views against the manual's 1000 W/m² clear sky), a daytime sky with sun disc or a daytime HDRI, EV cap +3 and a lighting finding above it, a light rig per room type with visible emissive fixtures, a shell material table per slot on CC0 PBR sets (ceiling plaster, worktops, fronts, ceramics, metals, tiles with grout displacement), sheen / coat / bevel node / AO / imperfections, fabric colour path, WB locked per project, 256-512 samples, 24 mm lens (28 in large rooms), eye 1.30-1.45 m, hall camera budget | 1.6, 1.1 |
| K6 outdoor and site | hedge row detector (≥ 5 equal circles, r ≤ 0.6 m, pitch ≤ 1.5 × diameter → `site.hedges` polyline with height class); tree height by crown class (no 4 m minimum under 1.5 m crowns); geometry-nodes hedge of leaf cards; trees as Poly Haven CC0 instances near cameras and Sapling-generated species-look trees elsewhere; grass clumps near cameras + displacement far; platforms per terrace/pool/parking polygon with retaining walls, kerbs and steps; pool coping, clipped basin, tiles, rippled water with absorption; sky with sun disc, skirt and a ground backdrop, haze as a closed mesh volume; facade kit (reveals, gutters, canopy, lights, railings); 2-D exterior camera search, hedges as low obstacles, one true aerial allowed | 1.7 |
| K7 licence plumbing | `licence_mode` setting (commercial | relaxed), `licence_flag` per catalogue entry (none, non_commercial, share_alike, no_derivatives, research_only, regional, tool_nc), `commercial_safe` derived, a `commercial-safe: yes/no` line per render with the flagged asset ids, ATTRIBUTION.md sections (tools, CC0/CC BY assets with authors, PoC-only assets, dataset notices), a CPU test that fits all three projects in commercial mode and asserts 0 flagged ids | §5 of the prompt |
| K8 measurement | frozen camera sets replayed by the render stage, metric scripts over the building JSON and logs, the committed rubric, baseline runs | §7 |

### 3.1 Approach A – quality first, licences relaxed behind a switch

Library: HSSD (CC BY-NC 4.0, gated) for every anchor type and all bath and kitchen fixtures, plus the ABO
remainder by size grid, Poly Haven at 2K with its trees and plants, ambientCG sets, TexVerse CC BY/CC0 picks
(NC/SA objects in relaxed mode only), the 18 NC/SA Objaverse entries already flagged; optional, user decision only:
3D-FUTURE via the user's own Tianchi account (never from mirrors), Maxtree Mediterranean tree packs ($175,
royalty-free, text unread), Hunyuan3D-Omni (EU-excluded). Vegetation: Poly Haven trees instanced, Infinigen and
Sapling trees, GN hedge and grass, site platforms, pools, sky (= K6). Placement: the M12 solver extended (= K3/K4).

Expected quality: living rooms with an L-sofa, rug, coffee table, armchairs facing the group, a TV unit and the
10-seat table at its drawn place; bedrooms with a real bed, bedding, mirrored nightstands, a wardrobe run; kitchens
and bathrooms with real product fixtures (HSSD) instead of boxes; exteriors with hedges, trees of plausible size,
platforms, pool coping and a sky. Target 3-4 of 5 per view (not 5: ABO is budget furniture with one material slot,
HSSD polycount and texture size are not stated).

Licence impact: in relaxed mode no render with an HSSD, NC or SA asset in view is commercially safe; the per-render
line and ATTRIBUTION.md say so; `licence_mode: commercial` refits from the same catalogue without them. The
critic's main objections: "relaxed for the PoC" is not a licence category (every render, catalogue statistic and size
bin derived with HSSD is a non-commercial artefact; a fit filter does not clean them); the proposal priced pods at
$2.09/h ($51.83 → $62 at the real price, 89 % of the remaining budget); its "vision quality ≤ 3 removes anchors"
gate reverses decision 1a and would shrink today's library by two thirds; 38 agent-days in a 14-day plan; no pod
renders in commercial mode, so the commercial product's before/after is never produced. Scores (critic): quality
3, licence safety 2, feasibility 2, cost realism 2, CLAUDE.md 2.

### 3.2 Approach B – commercial-safe maximum

Library: ABO remainder selected by the drawn size grid (up to 2,000 picks, 41.7 GB), Poly Haven at 2K/4K, ambientCG
300 sets, TexVerse CC BY/CC0 ∩ PBR pre-filtered by Objaverse++ (3,000 picks, 41.4 GB), OmniObject3D optional;
fixtures from Infinigen factories and our parametric kit; gated TRELLIS.2 fills (≤ 5 per type) with a Blender bake
replacing nvdiffrast; re-materialising ABO models with TRELLIS.2 texturing from their catalogue photos and Material
Anything. Vegetation: Sapling fork (primary) + Poly Haven hero trees + Infinigen plan B (= K6). Placement = K3/K4.
The switch exists but stays on `commercial_only: true`; nothing NC is downloaded.

Expected quality: living and bedroom anchors like A (ABO is the same source); kitchens and bathrooms depend on
Infinigen and generated fixtures, which is where the critic found the holes: the M12 P4 audit kept 0 of 3 Infinigen
toilets (2 "fix"), kitchen sinks, ovens and fridges; under B's own rule the 214 existing generated models are
nvdiffrast-tainted and unusable, which empties the fixture types (washbasin 5, toilet 1, bathtub 0, shower 0,
sink 0, fridge 1, washer 0 real-licence models left); the "Blender bake replacing nvdiffrast" is unbounded R&D;
Material Anything's base model is OpenRAIL++-M; auditing ~5,500 new models with two vision passes is ~10.6 pod
hours at the measured M12 rate (6.5 planned); downloads of tens of thousands of small files onto the network volume
are unmeasured (the volume writes small files at a few MB/s). Scores (critic): quality 3, licence 3, feasibility 2,
cost 2, CLAUDE.md 3; effort 44 agent-days.

### 3.3 Approach C – procedural and generative first

Library: parametric families v2 for every anchor type (sofa modules, beds with bedding, tables 0.8-3.4 m, wardrobe
runs, kitchen run v2 with door gaps and plinth, bath set v2 with basin bowls and taps) plus Infinigen factories;
60 generated anchors with TRELLIS.2 from ABO product photos sized from the listing (Blender bake replacing
nvdiffrast; Pixal3D A/B); ~150 ABO picks by size gap; ambientCG and Poly Haven for materials. Vegetation: Sapling
trunks + leaf-card crowns, GN hedges, Poly Haven hero trees (= K6). Placement: solver + designer terms; the VLM
picks among perspective previews of solver candidates (pairwise, both orders; no veto).

Expected quality: every drawn anchor is built (families cover any size), kitchens and bathrooms get detail (gaps,
taps, bowls, hobs); the look depends on the material and lighting track; "clean CG" rather than product photos.
Critic: Infinigen kitchen factories failed our audit; generated anchors are not commercial-safe and the bake is
unprototyped; Pixal3D is EU-flagged; "100 % anchors built by families" and "≥ 60 % anchors from real products"
contradict each other on real04 (≥ 20 of 43 anchors must be families); a meshed Sapling tree is 150k polygons
(100 unique trees ≈ 15 M polygons without instancing); 25-38 agent-days against a project that built 12 milestones
in 11 days; the rubric baseline was not committed (now it is: `results/review/m13_step0/`); the chair fix was wrong
(the 0.71 × 0.45 chairs fail the 10 % cap, not the wood re-sort; both causes exist for different chairs). Scores:
quality 3, licence 3, feasibility 2, cost 2, CLAUDE.md 3, effort 1 (very high).

## 4. Comparison

| | A quality first (relaxed) | B commercial-safe maximum | C procedural / generative first | **Recommended: core + B base + A layer (§5)** |
|---|---|---|---|---|
| Anchor models (living, bedroom) | HSSD + ABO: real products, many sizes | ABO + TexVerse: real products, thin at large sizes; module builders fill the rest | families + 60 generated | ABO by size grid + module builders; HSSD on top in relaxed mode |
| Bath and kitchen fixtures | HSSD real products (toilet 51, sink 109, tub 96, shower 62, fridge 58, stove 50, cabinets 288) | Infinigen (mostly failed the audit) + generated (nvdiffrast) + parametric | family v2 + Infinigen + generated | family v2 + the 6 audited Infinigen pieces + existing generated flagged `tool_nc`; HSSD in relaxed mode |
| Vegetation | Poly Haven + Infinigen + Sapling + GN | Sapling + Poly Haven + GN | Sapling + leaf cards + Poly Haven | Poly Haven instances + Sapling (installed add-on) + GN hedge and grass |
| Placement | solver + designer terms, VLM ranks marked top-downs | same | same, VLM picks on perspective previews | same; VLM ranks only after a measured A/B |
| Expected rubric mean (today 1.88) | 3.0-3.5 | 2.8-3.2 (fixtures weaker) | 2.8-3.2 (CG look) | 3.0-3.5 relaxed; 2.8-3.2 commercial |
| Commercial-safe renders | no while any HSSD/NC asset is in view; switchable | yes, except the nvdiffrast-era generated models | no until a clean bake exists | commercial mode: yes with the generated models flagged `tool_nc` (user decision D3); relaxed mode: no |
| Licence terms the user accepts | CC BY-NC 4.0 (HSSD), uploader-declared NC/SA, optional research-only / regional | none new (ABO conflict recorded) | nvdiffrast NC tool in the pipeline | CC BY-NC 4.0 for HSSD only, plus the `tool_nc` flag |
| New downloads | ~65 GB | ~99 GB | ~9 GB | ~25 GB (B base) + 38 GB (HSSD) |
| Audit load (models to render and judge) | ~2,900 | ~5,500 | ~400 | ~1,000-1,500 (ABO 400-600 by size grid, Poly Haven 100, HSSD 600-900 by type and size bin) |
| GPU at the real price ($2.49/h) | ~$62 + reserve | ~$46 + reserve | ~$50 + reserve | **$45-55 incl. baselines and one fix pod (§8)** |
| Effort (agent-days as proposed; the project's cadence is 1-2 days per milestone with parallel tracks) | 38 | 44 | 38 | core 5 parallel tracks ≈ 3 session days, library 1-2, runs 2-3 |
| Main risk | NC artefacts cannot be "switched" clean; budget | fixtures stay boxes; audit throughput | unproven bake; CG look | HSSD terms refused → fixtures stay families; price |
| CLAUDE.md changes | 6 | 5 | 8 | 7 (§9) |
| Critic scores (quality / licence / feasibility / cost / rules) | 3 / 2 / 2 / 2 / 2 | 3 / 3 / 2 / 2 / 3 | 3 / 3 / 2 / 2 / 3 | – |

Why not pick one of the three as written: all three were costed at $2.09/h and over-sized for the budget and the
cadence; A rests the library on a non-commercial dataset as the default, B leaves bathrooms and kitchens without
real models, C bets on an unprototyped export path. The core (§3.0) is where the images change most and it is
licence-neutral; the library choice is a separate decision with a switch.

## 5. Recommendation

**Build the core (§3.0, K1-K8) first; grow the library commercial-safe (B base); add HSSD as a switchable relaxed
layer (A) if you accept its CC BY-NC terms; keep generation (C) to module builders and a 10-model spike.**

Why this order: §1.1 shows the score is decided by coverage, choice, light and cameras, all in the core; the
library source only decides how good the fixtures and the large anchors can look. The core also makes the library
growth cheaper (size-grid picks instead of "20 per type", one audit pass, no re-sort surprises).

### 5.1 What gets built (step 2), in build order

| Phase | Tracks (parallel on CPU in this session; tests per track) | Pod | Output |
|---|---|---|---|
| 0 harness (day 1) | K7 licence flags, `licence_mode`, per-render line, ATTRIBUTION sections; K8 camera replay (`--cameras-from <manifest>`) and metric scripts over the committed files; the rubric committed (done) | – | baseline numbers for all three projects from committed files |
| 1 core (days 1-3) | K1 anchor ladder + size snap + module builders (wardrobe run, long table, L-sofa, kitchen run v2, bath set v2); K2 fit; K3 placement fixes + designer terms; K4 agent guards; K5 light/material/camera; K6 hedge/tree/site | P1 (RTX PRO 6000, ≤ 3 h): A/B on 8 fixed interior views (sun scale 100/300/1000 W/m², EV cap, light rigs, shell materials, 24 mm) and 3 exterior views (hedge, Poly Haven instances, Sapling trees, platforms, pools, sky), vegetation memory and time per view; GPU tests of the tracks | calibrated constants; a go/no-go per lever |
| 2 library (days 2-4) | ABO picks by size grid against the drawn demands of real02/03/04 (400-600 models), Poly Haven 2K + 20 trees + plants, ambientCG sets and atlases; HSSD picks by type and size bin (600-900) **only after D2**; audit gates: known units for anchors, PBR maps recorded, material tags judged for every entry, chaise side, size-bin coverage; one vision pass (decision 1a stays) | P2 (≤ 3.5 h): downloads to `/workspace/assets` (speed probe first, 15 min), audit renders with the scale figure, code checks, vision pass, decisions, gaps, catalogue | catalogue with `licence_flag`, coverage per drawn demand |
| 3 proof (days 4-7) | fixes from P1/P2; the three full runs with 3 agent rounds and the frozen cameras + the new camera policy as a second set; metrics; before/after sheets | B0 baselines real02 + real03 with M12 code (optional, D6), P3 real04, P4 real02 + real03, P5 one fix round | `docs/milestone13.md` §12 results, `docs/progress.md`, GPU log |

Cut line if money or time runs short (in this order, last first): HSSD layer → TexVerse → generated spike →
facade kit → designer score terms beyond R3/R6/R12 → the second camera set.

### 5.2 What the AI decides and what code decides (unchanged in spirit from M12, sharper in practice)

| Decision | Code | AI (Qwen3.8-27B-FP8, temperature 0, strict JSON) |
|---|---|---|
| type of a drawn footprint | twin room / other level / block name / missing group member first | plan-crop typing only when the rules fail (two passes where no code check exists) |
| sizes | product-size snap, uniform scale, module assembly | none |
| group membership, positions, fronts, rugs, cameras, lights | solver, checks, rules | none; ranks top-3 candidates on marked images only after a measured A/B shows it beats the code score |
| library model per piece | rank + caps + ladder | asset pins (skip the style filter) |
| agent edits | validators; accepted only when the finding is gone | proposes retype / not-furniture / swap / asset job where a tool exists |
| final look check | cross-check with the building JSON | one pass per final view; findings route to the stage, never auto-fixed |

### 5.3 Drawn furniture (CLAUDE.md) under this plan

Fixed equipment stays locked (moves ≤ 0.5 m for clear errors). Drawn furniture keeps `drawn_type`,
`drawn_footprint`, `drawn_front_deg`, `drawn_height`; three things change and need your OK (§9): (1) a drawn anchor
is always built (ladder), (2) a drawn group may be re-solved as a unit around its drawn anchor place when the anchor
is missing or misread, every member bounded to 0.5 m from its drawn centre and logged `adjusted_by_ai`, (3) a drawn
size outside the product grid is snapped to the nearest real product before the fit (already allowed, now done for
furniture, not only fixtures). `keep` and `furnished_rooms_keep_size` switch (2) and (3) off.

## 6. The licence switch (common to every approach)

- Catalogue: every entry carries `licence`, `licence_url`, `licence_declared_by` (publisher | uploader),
  `licence_flag` ∈ {none, non_commercial, share_alike, no_derivatives, research_only, regional, tool_nc},
  `commercial_safe` (derived: flag none and no NC tool in the export chain), `attribution`.
- Setting: `library.licence_mode: commercial | relaxed` in the run config (env `WENART_LICENCE_MODE` overrides).
  `commercial` (default) makes `catalog.usable` (`catalog.py:596`) accept only `commercial_safe: yes` entries.
  `relaxed` (PoC, user OK per project) accepts NC, SA, research-only and regional flags too; `no_derivatives` is
  never used (we scale and re-texture). Flipping back re-runs the fit, the layout completion and the renders; the
  volume is untouched (nothing deleted).
- Honest limits of the switch (critic of A): statistics and size bins computed from NC assets stay NC artefacts;
  the agent's `asset_pin` overrides and memory of a relaxed run are dropped on a mode flip (test); a project rendered
  in relaxed mode is reported as such in every line.
- Per render: `final_report.md` and the render manifest carry `commercial-safe: yes` or `commercial-safe: no
  (flagged assets: ids)`; a view with any flagged asset in its object-index pass is `no`.
- `ATTRIBUTION.md` (already written per project; extended): 1 tools and generators with licences (incl. the DINOv3
  acknowledgement and the Poly Haven API credit), 2 CC0 / CC BY assets with author, source, licence and changes,
  3 PoC-only assets (NC / SA / research-only / regional / tool_nc) with the reason, 4 dataset notices (ODC-By).
- `tool_nc`: the 281 generated models were exported with nvdiffrast (NC). In `commercial` mode they are excluded
  unless you decide otherwise (D3); in `relaxed` mode they are used and listed under 3.
- Tests: fit all three projects in `commercial` mode and assert 0 flagged ids; a relaxed run followed by a mode flip
  leaves no flagged id in `building_final.json`, `overrides.json` or `memory.json`.

## 7. Measurable before/after (same views)

Baselines: real04 = the committed M12 run; real02 and real03 = the committed M11 runs (history) **and**, if D6 is
yes, one M12 baseline run each (pod B0) so that both sides of the comparison use the same solver and library rules.
"Same views": the render stage gets the committed camera records (`--cameras-from`), so set 1 of the "after" is
rendered from the old camera positions with the old lens; set 2 uses the new camera policy (24 mm, 1.30-1.45 m).
A frozen camera that ends up inside a newly built piece is moved by the free-floor rule and marked.

| # | Metric (script over building_final.json, log.json, final_manifest.json; definitions fixed in the script) | real04 before (M12) | Target |
|---|---|---|---|
| 1 | drawn anchors built (sofa, sofa_corner, bed_double, table_dining, wardrobe, desk): share | 11 of 35 (31 %) | 100 % (library or module or family) |
| 2 | drawn pieces in the scene (build true and method ≠ none) | 128 of 240 (53 %) | ≥ 90 % |
| 3 | pieces with `asset.method: none` | 43 | 0 |
| 4 | parametric share of built pieces (58 of 177 built; 115 of 246 fitted pieces when the unbuilt ones count); grey boxes | 33 % (47 %); 0 | ≤ 25 % (runs, stairs, families only); 0 |
| 5 | rooms with a complete group set (bed + 2 nightstands + wardrobe; sofa + coffee table + tv unit + rug; table + chairs; counter + sink + hob + fridge; toilet + basin + shower/tub) | bedrooms 4/8, living 0/4, kitchens 0/4, bathrooms 8/10 | ≥ 90 % of furnished main rooms |
| 6 | last-round findings F8 / S2 (> 3 cm) / G10 / LG | 38 / 1 / 18 / 66 | ≤ 5 / ≤ 3 / report-only / ≤ 5 |
| 7 | accepted agent edits whose finding is gone next round | 20 of 160 | ≥ 60 % (or the agent is off) |
| 8 | built library pieces: top model share; distinct models; units unknown; stretch > 5 %; audit quality ≤ 3 | 31 %; 26; 50 %; 46 %; 52 % | ≤ 15 %; ≥ 60; ≤ 10 %; ≤ 10 %; ≤ 25 % |
| 9 | interior views at EV ≥ +5; EV median gap between lit and daylight rooms | 9 of 44; 7.2 EV | 0; ≤ 2 EV |
| 10 | shell slots on PBR sets with normal + roughness; fabric colour of the brief applied to upholstered pieces | not recorded; 0 of 18 | ≥ 90 %; 100 % |
| 11 | drawn trees built as real or generated geometry; hedges from the drawn rows; black pixels in the site view | 0 of 100; 0; 29 % | 100 %; 2; 0 % |
| 12 | exterior views rendered of planned | 4 of 7 | 7 of 7 |
| 13 | views in halls / with ≥ 50 % bare wall | 12 of 48 | ≤ 4 |
| 14 | `in_json_not_rendered` mismatches of the final check | 18 in 10 views | 0 |
| 15 | rubric score (same reviewer rubric as `results/review/m13_step0/`, applied by the same procedure to the after images; plus your own look at 12 views per project) | mean 1.88; 20 views at 1 | mean ≥ 3.0; 0 at 1; ≥ 25 % at 4-5 |
| 16 | commercial-safe line present; ATTRIBUTION lists every flagged asset | – | 100 %; 0 missing (test) |
| 17 | minutes and USD per full run | 114 min, $4.72 | ≤ 150 min, ≤ $6.50 at $2.49/h |

The VLM judges stay out of the score (M12 bake-off and SceneCritic: at or near chance on layouts); the rubric is
applied the same way before and after, and the per-view JSON is committed next to the images.

## 8. GPU plan and budget (real prices: RTX PRO 6000 $2.46-2.60/h since 9 Oct, median $2.49; RTX 5090 $1.18/h, 32 GB)

Spent $130.54 of $200; $69.46 left. Limits: $5/GPU-h, $30/day, 4 h per pod, one pod at a time; every pod below is
over $5 worst case and needs your OK (`--over-5-ok` per pod, or one OK for the list).

| Pod | Work | GPU | Hours | USD at $2.49 |
|---|---|---|---|---|
| P1 | lever A/B: 8 interior + 3 exterior fixed views × variants (sun, EV cap, rigs, materials, lens; hedge, trees, platforms, pools, sky), vegetation memory and time, GPU tests of the core tracks | PRO 6000 | 2.5 | 6.2 |
| P2 | downloads (speed probe first), audit renders + code checks + one vision pass for ~1,000-1,500 models (ABO, Poly Haven, HSSD if D2), decisions, gaps, catalogue | PRO 6000 (52 GB judge) | 3.5 | 8.7 |
| B0 | baselines real02 + real03 with the M12 code (optional, D6) | PRO 6000 | 3.5 | 8.7 |
| P3 | full run real04 (3 agent rounds, frozen + new cameras, 256-512 spp) | PRO 6000 | 2.5 | 6.2 |
| P4 | full runs real02 + real03 | PRO 6000 | 4.0 | 10.0 |
| P5 | one fix round (the worst project) + metric renders | PRO 6000 | 2.5 | 6.2 |
| Total | | | 18.5 | **46.0** (37.3 without B0) |
| Reserve for one failed pod (M12 had 3 paid failures in 14 pods) | | | 3 | 7.5 |

So $46-54 of $69.46; two failures or a second fix round break the $200 cap. Ask: raise the project total to $230
(D6). Daily cap: two pods per day at most ($18-19). Volume: +25 GB (B base) or +63 GB (with HSSD) on ~280 GB free.
Model caches stay on the container disk (TRELLIS.2 16 GB, Z-Image 33 GB, Qwen3.8 31 GB, bpy 4.2 wheel 0.5 GB).

## 9. `CLAUDE.md` wording (proposals; nothing is applied before your OK)

1. **Library rules** (replace the block): "Only audited library models (`keep`, `fix`) and audited module or
   parametric families are used. Every catalogue entry carries `licence`, `licence_url`, `licence_declared_by`,
   `licence_flag` (`none` | `non_commercial` | `share_alike` | `no_derivatives` | `research_only` | `regional` |
   `tool_nc`), `commercial_safe` and `attribution`. `library.licence_mode: commercial` (default) uses only
   `commercial_safe: yes` entries. `relaxed` (PoC only, user OK of <date> per project) may use non-commercial,
   share-alike, research-only and regional assets; no-derivatives assets are never used. Every render carries
   `commercial-safe: yes|no` with the flagged asset ids; every run writes `ATTRIBUTION.md` (tools, assets with
   authors, PoC-only assets, dataset notices). Research-only data sets that forbid redistribution (3D-FUTURE,
   3D-FRONT) are not used. Nothing is deleted from the volume without the user's OK. When no audited model fits a
   drawn anchor, the run builds it anyway (nearest model within the caps → module builder with real proportions →
   parametric family) and writes a `library gap` finding; a drawn anchor is never left out and never built as a grey
   box." (This reverses M12 D14 "never a parametric sofa, bed or table".)
2. **Furniture rules**, add: "A drawn furniture size outside its type's product range (a block with its neighbours,
   a split artefact) is snapped to the nearest real product size before the fit (`adjusted_by_ai`, `drawn_footprint`
   kept, plan crop as evidence). A drawn group (a table with its chairs, a sofa with its armchairs and coffee table,
   a bed with its nightstands) is one unit: when its anchor is missing, misread or fails the checks, the solver
   re-places the group around the drawn anchor centre; every member moves at most 0.5 m from its drawn centre and
   is logged `adjusted_by_ai`. A drawn piece that cannot be built is never an obstacle for its own group. With `keep`
   or `furnished_rooms_keep_size` the snap and the group re-solve are off."
3. **Furniture rules**, add: "An untyped drawn footprint is typed by code first: the same footprint in the twin
   room or on another level (within 1 cm), the block name, or the room's missing group member of that size
   (`inferred`, with the evidence); the AI types the rest from the plan crop."
4. **Furniture rules**, edit "the AI chooses the program and between solver candidates, never coordinates" to "the
   AI chooses the program; the code score chooses between solver candidates unless a measured test shows the vision
   model ranks marked candidate images better; the AI never gives coordinates and never judges a bare top-down."
5. **New section "Vegetation and site rules"**: "A row of ≥ 5 drawn tree symbols of equal radius ≤ 0.6 m at a pitch
   ≤ 1.5 × their diameter is a hedge; single symbols are trees; tree height follows the crown radius by size class
   (a crown under 1.5 m is a shrub). Every tree, shrub, hedge and lawn is a real model or generated geometry with
   leaf textures, never a primitive; species not named in the documents are `inferred` and named in the report.
   Terraces, pools and parking get one level each with retaining edges; pools get coping and water; the sky, the
   sun and the horizon are always in the image. Vegetation and site assets are audited like furniture."
6. **Evidence rules**, add: "An agent edit is accepted only when the finding it targets is gone in the dry re-check
   and no new critical finding appears; 'edits accepted' is no success metric, 'findings removed' is. Building-wide
   edits (roof, terrain, site, exterior cameras) come only from the building session."
7. **GPU limits**: "Project total: $230 (raised from $200 on <date>, user OK, Milestone 13)"; and in "Where you
   run": "RTX PRO 6000 ≈ $2.5/h (live price), RTX 5090 ≈ $1.2/h (32 GB: no 27B server)". Engineering conventions:
   "Open-weight models and open-source tools only; commercial-safe licences by default (`licence_mode:
   commercial`); other licences only in `relaxed` mode, flagged in the catalogue, in `docs/plan.md` and in
   `ATTRIBUTION.md`. GPL tools (Blender, its add-ons, LibreDWG, Infinigen's GPL submodule) run as installed
   programs; no GPL code is copied into this repository."

## 10. Decisions for you

| # | Question | My recommendation |
|---|---|---|
| D1 | Approach: core + commercial-safe base + HSSD relaxed layer (§5)? Or B only (commercial-safe), or A or C as written? | core + B base + A layer |
| D2 | HSSD (CC BY-NC 4.0): accept the terms with the Hugging Face account behind the pod's `hf_token` and allow HSSD assets in `relaxed` mode (renders with them are `commercial-safe: no`)? | yes for the PoC; it is the only real-product source for bath and kitchen fixtures |
| D3 | The 281 existing generated models (TRELLIS.2, exported with the NC tool nvdiffrast): keep them usable in `commercial` mode with the `tool_nc` flag (PoC), or exclude them (then fixtures are families and Infinigen's 6 audited pieces only in commercial mode)? | keep with the flag for the PoC; replace the export before any commercial use (already noted in `docs/plan.md`) |
| D4 | Reverse M12 D14: a drawn anchor is always built (ladder: model → module builder → family), never left out? | yes |
| D5 | Drawn group as a unit with a 0.5 m per-member bound, and product-size snap for furniture (§9.2, §9.3)? | yes |
| D6 | Budget: raise the project total to $230; OK for the pods of §8 (each over $5); run the M12 baselines B0 for real02/real03 ($8.7) or compare against the committed M11 images only? | raise to $230; run B0 |
| D7 | `CLAUDE.md` wording 1-7 (§9)? | yes, with your edits |
| D8 | Camera policy 24 mm / 1.30-1.45 m as the new default (set 2 of the after images)? | yes |
| D9 | Paid or external items: Maxtree Mediterranean trees ($175, terms unread), BlenderKit (terms unread), 3D-FUTURE (research-only via your own Tianchi account)? | no to all three for M13 |
| D10 | AI polish stays off in M13 (the Cycles fixes come first)? | yes |

## 11. What could not be verified in this session (kept as risks)

HSSD polycount and texture resolution (card does not state them; the gate hides the files); TexVerse furniture
counts per type (metadata readable on the pod only); 3D-FUTURE licence text (official page blocked; secondary
only); BlenderKit and Maxtree terms (sites blocked); the sun W/m² value that lands lit and daylight rooms within
2 EV (P1 measures it); Infinigen per-tree time and the pod's Python version for the 3.11 venv (exists since M12
P4); Poly Haven tree render memory with 100 instances (P1); download speed of small files to the network volume
(speed probe in P2); IES file sources; whether the two M12 real02/real03 outputs still exist anywhere (removed on
12 Oct per the cleanup, so B0 is the only like-for-like baseline); the cause of the too-high bathroom art (B12).

GPU cost of step 0 and step 1: $0.00 (no pod). Project total unchanged: $130.54 of $200. No pod is running.

## 12. Decisions of 12 Oct 2026 (user) and the build

| # | Decision | What it means for the build |
|---|---|---|
| D1 | "go to relaxed" | `licence_mode: relaxed` is the Milestone 13 default: core + commercial-safe base + the HSSD layer; the switch and the per-render line are built anyway |
| D2 | HSSD: yes | HSSD (CC BY-NC 4.0, gated) is downloaded and audited in pod P2; the user accepts the terms at `https://huggingface.co/datasets/hssd/hssd-models` with the Hugging Face account whose token is the pod's `hf_token` secret (user, 12 Oct 2026: "I accept this"); P2 checks the gate at run time and skips the HSSD step with a clear log line on a 403 |
| D3 | keep flagged | the 281 nvdiffrast-era generated models stay usable with `licence_flag: tool_nc`; in `commercial` mode they are excluded |
| D4 | yes, "but we need a good model" | the fallback ladder is built, and the fallback must look like a real product: module builders from real module sizes with PBR slots, parametric families v2 with PBR, bevel and real proportions; every piece built below the library level is listed in the report so the gap can be closed with a real model later |
| D5 | yes | drawn groups as units (0.5 m per-member bound), product-size snap for furniture; off with `keep` / `furnished_rooms_keep_size` |
| D6 | raise to $300 | project total $300 (CLAUDE.md); the pods of §8 are approved. **Later on 12 Oct 2026 the user cancelled the M12 baselines ("no need m12 baselines, you can use the m11 as base line, stop the pods")**: the baseline of real02 and real03 is the committed M11 run (`results/renders/<p>/scene_manifest.json` carries its cameras), the baseline of real04 is the committed M12 run (no camera records committed: compared by camera name and room); pod B0a was stopped after 3 minutes (§14) |
| D7 | yes with my edits | `CLAUDE.md` updated (this commit) |
| D8 | no | cameras keep the M11 policy (18/16 mm at 1.25 m, hall views as today); the before/after uses the same camera records on both sides; the exterior camera bugs (site view below the horizon, dropped views behind the hedge) are still fixed because they are bugs, not policy |
| D9 | hold the paid ones | no Maxtree, no BlenderKit, no 3D-FUTURE in Milestone 13 |
| D10 | yes | AI polish stays off |

Build (step 2) follows in §13 (contracts) and §14 (build log).

## 13. Contracts of the build (frozen 12 Oct 2026; only the lead edits this section)

Scope: the common core K1-K8 of §3.0 under the decisions of §12 (relaxed licence mode, HSSD layer, fallback ladder
with good-looking fallbacks, drawn groups as units, M11 camera policy kept, polish off). Eight tracks build in
parallel on disjoint files; the lead integrates, runs the CPU suite, commits and pushes. Pods only after the CPU
suite is green (§13.6).

### 13.1 Tracks and file ownership

| Track | Builds | Owns (only this track edits) | Tests (existing + new) |
|---|---|---|---|
| **T1** fit and licence rules | K2; K1 size snap and ladder decision; K7 catalogue side: `licence_mode`, `licence_flag_of`, `commercial_safe`, `usable(entry, mode)`; wood re-sort removed; rank by real product, known units, audit quality and faces (tie-breaks, not gates); uniform scale to the drawn width; design tags as preferences; pins skip the style filter; diversity penalty per room and project; `project.licence_mode` written into the building | `wenart/furniture/fit.py`, `catalog.py`, `sizes.py`, `wenart/furniture/__main__.py`, `wenart/recognition/size_table.yaml`, the catalogue files only for the new licence fields of existing entries (`catalog_library.json`, `catalog.json`: a script, no hand edits) | `tests/test_furniture_fit*.py`, `test_library_filter.py`, `test_library_sizes.py`, `test_scene_fit.py`; new `tests/test_m13_fit.py` |
| **T2** module builders and families v2 | K1 fallback look (D4): module builders with real module sizes and PBR slots (wardrobe run, long table + chairs, L-sofa from a straight module and a chaise, kitchen run v2, bath set v2: vanity + basin + mirror, shower + tray + glass), parametric families v2 (bed with headboard and bedding, sofa, armchair, table, nightstand, desk, shelving, TV unit) with bevels, real proportions and material slots; grey boxes never | `wenart/blender/parametric.py`, `furniture.py`, `proxies.py`, `textiles.py`, new `wenart/blender/modules.py` | `tests/test_blender_furniture.py`, `test_blender_bedframe_decor.py`, `test_cabinets.py`; new `tests/test_m13_modules.py`, `tests/gpu/test_m13_modules.py` |
| **T3** placement | K3: code-first typing (twin room / other level / block name / missing group member), drawn group as one unit (0.5 m per-member bound), room-type aliases, tiered minimums and NKBA soft in small kitchens, S2 tolerances 3 cm fixtures / 5 cm soft seating, F8 names the missing anchor, F2 on every drawn piece, designer terms R3, R6, R12-R14 as data, the rug as a group member, unbuilt anchor never an obstacle | `wenart/furniture/solver.py`, `program.py`, `groups.py`, `groups.yaml`, `group_checks.py`, `infer.py`, `complete.py`, `layout.py`, `placer.py`, `plausibility.py`, `locked.py`, `wenart/blender/scene_checks.py`; the `solve_room` line of `tests/test_m12_contracts.py` | `tests/test_groups*.py`, `test_solver_rooms.py`, `test_infer.py`, `test_complete*.py`, `test_scene_checks.py`, `test_group_checks.py`, `test_layout.py`, `test_plausibility.py`; new `tests/test_m13_placement.py` |
| **T4** agent loop | K4: an edit is accepted only when its finding is gone in the dry re-check and no new critical finding appears; tools offered by cause; building-wide tools only in the building session; idempotent `set_exterior`; `retype_piece` builds the piece (through T1's fit); `place_group` reuses the drawn group; `swap_model` never for S2 < 3 cm; 3 rounds; the vision critic only where a tool exists; metric "findings removed" | `wenart/agent/**`, `wenart/furniture/edit_ops.py`, `wenart/furniture/prompts.py`, `wenart/furniture/schemas.py` | `tests/test_agent_*.py`, `test_edit_ops.py`, `test_groups_edits.py`, `test_run_agent*.py`; new `tests/test_m13_agent.py` |
| **T5** light, materials, render, camera replay | K5 without the lens change (D8): sun strength constant in the hundreds of W/m² behind an A/B switch, daytime sky with sun disc (exterior world), EV cap +3 with a `lighting_dark` finding, light rig per room type with visible emissive fixtures, shell material table per slot on the CC0 sets (ceiling plaster, worktops, fronts, ceramics, metals, tiles with grout), sheen / coat / bevel / AO / imperfections, fabric colour path, WB locked per project; K8 camera replay `--cameras-from`; the lever A/B job | `wenart/blender/lighting.py`, `materials.py`, `looks.py`, `render.py`, `build.py`, `cameras.py`, `camsearch.py` (replay only, no policy change), `wenart/run/ab.py`, `wenart/run/stages.py`, `wenart/run/plan.py`, new `scripts/jobs/levers_ab.sh`, `wenart/style/**` (fabric colour path) | `tests/test_blender_render.py`, `test_blender_materials.py`, `test_blender_look.py`, `test_look_m6.py`, `test_blender_cameras.py`, `test_run_ab.py`, `test_run_stages.py`, `test_run_plan.py`, `test_style*.py`; new `tests/test_m13_light.py`, `tests/gpu/test_m13_light.py` |
| **T6** outdoor and site | K6: hedge-row detector → `site.hedges`; tree height by crown class; vegetation module (Poly Haven instances near cameras, Sapling species-look trees elsewhere through the installed add-on, geometry-nodes hedge of leaf cards, grass clumps near cameras and displacement far); platforms per terrace / pool / parking with retaining walls, kerbs and steps; pool coping, clipped basin, tiles, water; skirt and ground backdrop, haze as a closed mesh volume; facade kit (reveals, gutters, canopy, lights, railings); exterior camera bugs (site view below the horizon, views dropped behind the hedge; hedges as low obstacles; one true aerial) | `wenart/blender/site.py`, `exterior.py`, `exterior_checks.py`, `facade.py`, `copies.py`, `roof.py`, new `wenart/blender/vegetation.py`, `wenart/sheets/exterior.py`, new `scripts/pod_setup_vegetation.sh`, new `scripts/jobs/site_ab.sh` | `tests/test_blender_site.py`, `test_blender_exterior.py`, `test_sheets_exterior.py`, `test_site_buildings.py`, `test_gate_exterior.py`, `test_m11_exterior.py`; new `tests/test_m13_site.py`, `tests/gpu/test_m13_site.py` |
| **T7** library growth and audit | §5.1 phase 2: drawn demands of real02/03/04 → size-grid picks; ABO by size grid (400-600), Poly Haven 2K + trees + plants, ambientCG sets; HSSD picks by type and size bin (600-900, CC BY-NC 4.0, gated, `HF_TOKEN`); audit gates (known units for anchors, PBR maps recorded, material tags, chaise side, size-bin coverage), one vision pass; gap report by drawn demand; `library_growth.sh` steps `ingest-hssd`, `demands`, `size-grid` | `wenart/assets/**` (new `hssd.py`, `audit/demands.py`), `wenart/assets/audit.yaml`, `scripts/jobs/library_growth.sh`, `scripts/jobs/library_audit_*.sh`, `results/library/**` | `tests/test_library_growth*.py`, `test_audit_*.py`, `test_assets.py`, `test_abo*.py`, `test_objaverse*.py`, `tests/gpu/test_library.py`; new `tests/test_m13_library.py` |
| **T8** licence plumbing, attribution, report, metrics | K7 output side: `commercial-safe: yes | no (flagged assets: ids)` per render in `final_report.md` / `.json`, ATTRIBUTION.md sections 1-4, "built below library level" list per project; K8 metrics: `wenart/report/metrics13.py` (the 17 metrics of §7 over building JSON, logs and manifests, before vs after), before/after sheets per camera; the commercial-mode test over the three committed buildings | `wenart/report/**`, `wenart/run/copy.py`, `wenart/run/pack3d.py`, new `wenart/report/metrics13.py`, new `wenart/report/sheets13.py` | `tests/test_report*.py`, `test_run_copy.py`, `test_pack3d.py`; new `tests/test_m13_report.py` |
| Lead | contracts, schema, defaults, briefs, job wiring, integration, pods, docs | `CLAUDE.md`, `docs/**`, `wenart/schema/building.schema.json`, `wenart/defaults.yaml`, `wenart/brief.py`, `projects/*/brief.yaml`, `scripts/gpu_run.py`, `scripts/jobs/*.sh` (not `library_*`, `levers_ab.sh`, `site_ab.sh`), `scripts/pod_setup*.sh` (not `_vegetation`), `tests/test_m13_contracts.py`, `tests/test_gpu_run.py` | – |

Rules for every track: no edit outside its files (a needed change elsewhere goes into the track's report; the lead
decides); no git commands that change state (the lead commits); `pytest` on its own tests plus
`tests/test_m11_contracts.py tests/test_m12_contracts.py` green; new tests fail on the old code; nothing invented:
model ids, licence texts, Blender API names verified in the source or the official docs; no key or token printed.

### 13.2 Frozen interfaces (`tests/test_m13_contracts.py`, written by the lead after the tracks)

| Module (owner) | Functions and constants | Used by |
|---|---|---|
| `wenart/furniture/catalog.py` (T1) | `LICENCE_MODES = ("commercial", "relaxed")`; `LICENCE_FLAGS = ("none", "non_commercial", "share_alike", "no_derivatives", "research_only", "regional", "tool_nc")`; `licence_mode(brief=None, env=None) -> str` (env `WENART_LICENCE_MODE` > brief `library.licence_mode` > `commercial`); `licence_flag_of(entry) -> str` (from `licence_flag`, the licence text, `source` generated + nvdiffrast → `tool_nc`); `commercial_safe(entry) -> bool` (flag `none`); `usable(entry, mode="commercial") -> bool`; `unusable_reason(entry, mode="commercial")` | T1 fit, T4 `swap_model` / `retype_piece`, T7 audit, T8 report |
| `wenart/furniture/sizes.py` (T1) | `snap_size(ftype, footprint, height=None) -> {footprint, height, product, changed, reason}` (nearest real product of the type; `changed` false inside the range); `PRODUCT_GRID` from `size_table.yaml` | T1 fit, T3 typing and groups |
| `wenart/furniture/fit.py` (T1) | `fit_piece(piece, catalog, cap=NON_UNIFORM_CAP, *, mode="commercial", ...)`, `fit_building(building, catalog, *, mode=None, ...)` (mode None = `project.licence_mode` or `licence_mode()`); the result's `asset.method` ∈ `library | module | parametric | none`, `asset.ladder = [{step, result, reason}]`, `asset.licence`, `asset.licence_flag`, `asset.commercial_safe`; `piece.library_gap` names the step used; `none` only for not-furniture, removed or `keep` pieces that are not built | T2 (reads `asset.method`, `asset.module_plan`), T3, T4, T8 |
| `wenart/blender/modules.py` (T2) | `module_plan(piece, style=None) -> dict | None` (pure, no bpy: `{builder, modules: [{kind, size_m: [w, d, h], pos_m: [x, y], rot_deg, material}], footprint_m, height_m, products: [names]}`; None when no module builder exists for the type); `MODULE_BUILDERS` (type → builder name); `build_module(plan, piece, materials)` (bpy, returns the object) | T1 (ladder step 2 decides on `module_plan` is not None), `furniture.py` |
| `wenart/blender/parametric.py` (T2) | `FAMILY_TYPES` (types with a v2 family); every builder keeps its signature; the output objects carry `wenart_method = "parametric"` and real material slots (never a flat grey default) | `furniture.py`, T5 materials |
| `wenart/furniture/infer.py` (T3) | `type_by_code(building, piece) -> {type, method: twin | level | block | group_member, evidence, confidence} | None` | T3 (ingest and completion), T4 `retype_piece` |
| `wenart/furniture/groups.py` (T3) | `drawn_groups(building, room_id) -> [{anchor_id, members: [ids], centre, template}]`; `GROUP_MEMBER_MOVE_MAX_M = 0.5` | T3 solver, T4 `place_group` |
| `wenart/furniture/solver.py` (T3) | `solve_room(building, room_id, program=None, *, k=3, fixed_ids=None, drawn_group=None) -> [Candidate]` (the M12 signature + `drawn_group`); `apply_candidate` unchanged; an unbuilt drawn anchor is not an obstacle for its own group | T3, T4 |
| `wenart/blender/scene_checks.py` (T3) | `TOLERANCES["overlap_fixture"] = 0.03`, `TOLERANCES["overlap_soft"] = 0.05` (S2 by class) | T4, build |
| `wenart/furniture/edit_ops.py` (T4) | `apply_edit`, `dry_run(building, edit, *, catalog=None)`, `allowed_edits` keep their signatures; `retype_piece` refits through `fit.fit_piece`; `swap_model` refuses S2 < 0.03 m with a reason | T4 |
| `wenart/agent/loop.py` (T4) | `accept_edit(before, after, edit) -> (bool, reason)` (pure); `MAX_ROUNDS = 3`; `tools_for_finding(finding) -> [tool]` (by cause) | T4, tests |
| `wenart/blender/lighting.py` (T5) | `SUN_STRENGTH_WM2` (the calibrated constant; the A/B variants `WENART_LIGHT_VARIANT`); `room_rig(room_type) -> [fixtures]`; `build_lighting(...)` keeps its signature | build |
| `wenart/blender/materials.py` (T5) | `shell_material(slot, style, assets) -> material` (slots `ceiling, worktop, front, ceramic, metal, tile, plaster`); `exterior_world_nodes(..., sun_disc=True, sun_elevation_deg, sun_azimuth_deg)` | build, T6 (sky via the existing call) |
| `wenart/blender/render.py` (T5) | `EXPOSURE_LIMITS = (-2.0, 3.0)`; a `lighting_dark` entry in the render manifest when the metered EV would pass the cap | T8 report |
| `wenart/blender/build.py` (T5) | `--cameras-from <scene_manifest.json>`: cameras recreated from the records (name, location, target or rotation, lens, sensor, clip), scene manifest camera `source: "replayed"`; the search runs only for cameras not in the file; `--cameras-extra` adds the searched set as well | T8 sheets, pods P3-P5 |
| `wenart/run/ab.py` (T5) | `prepare_m13(project, project_out, commit) -> dict` (the committed `scene_manifest.json`, `render_manifest.json` and previews of the baseline run into `out/ab/m13/`); `cameras_check` reused | lever A/B, before/after |
| `wenart/sheets/exterior.py` (T6) | `hedge_rows(circles) -> [{polyline, radius_m, pitch_m, count, height_class}]` (≥ 5 equal radii ≤ 0.6 m, pitch ≤ 1.5 × diameter); written to `site.hedges` | T6 site |
| `wenart/blender/site.py` (T6) | `tree_height(crown_radius_m) -> (height_m, size_class)` (shrub < 1.5 m crown; small 1.5-2.5 → 4-6 m; medium 2.5-4 → 6-10 m; large > 4 → 10-15 m); `platforms(site) -> [{polygon, z, kind, edge}]`; `build_site(...)` keeps its signature | build |
| `wenart/blender/vegetation.py` (T6) | `tree_object(species, height_m, seed, near_camera: bool)`, `hedge_object(hedge)`, `grass_patch(polygon, density)`; `SPECIES` (name → source: polyhaven id or sapling preset); never a primitive; GPL add-ons are called through `bpy.ops`, no add-on code in the repo | site |
| `wenart/blender/copies.py` / `exterior.py` (T6) | `site_view` keeps the horizon in frame (pitch ≤ 28°, height so the horizon is above the lower third); `view_check` treats `site.hedges` as obstacles of their height; one aerial view allowed | build |
| `wenart/assets/hssd.py` (T7) | `hssd_candidates(demands, n_per_bin) -> [ids]`, `download(ids, dest, token_env="HF_TOKEN")` (huggingface_hub, gated repo `hssd/hssd-models`); entries `licence: "CC-BY-NC-4.0"`, `licence_flag: "non_commercial"`, `licence_declared_by: "publisher"`, `licence_url: "https://huggingface.co/datasets/hssd/hssd-models"` | growth job |
| `wenart/assets/audit/demands.py` (T7) | `drawn_demands(building_paths) -> [{type, w, d, h, count, projects}]`; `size_grid(demands) -> {type: [bins]}`; `coverage(catalog, demands, mode) -> {type: {bin: n}}` | T7 picks and gap report, T8 report |
| `wenart/run/copy.py` (T8) | `attribution_text(title, credits, *, mode="commercial") -> str` with the sections 1 tools and generators, 2 CC0 / CC BY assets, 3 PoC-only assets with the reason, 4 dataset notices; `project_credits` adds `licence_flag`, `commercial_safe` | run |
| `wenart/report/final.py` (T8) | per view `commercial_safe: {safe: bool, flagged: [asset ids]}` from the scene manifest's objects × the catalogue flags × the view's `index_values`; `final_report.md` line `commercial-safe: yes` / `no (flagged assets: …)`; section "Built below library level" (module / parametric pieces of furniture types) | report |
| `wenart/report/metrics13.py` (T8) | `metrics(project_out, baseline_out=None) -> dict` (the 17 metrics of §7, each `{value, baseline, unit, source}`); CLI `python -m wenart.report metrics13 --out <project_out> [--baseline <dir>] --json <path>` | §14 |
| `wenart/report/sheets13.py` (T8) | `sheets(project_out, baseline_out, out_dir)`: one side-by-side JPEG per camera (before | after, same view) | §14 |

`Violation = {check, severity, target, room_id, message, metrics}` stays the one finding format.

### 13.3 Data between the tracks (schema fields added by the lead now, all optional)

- Building JSON: `project.licence_mode` (T1 writes it in the fit stage; later stages read it, never the brief);
  `furniture[].asset.{method, licence, licence_flag, commercial_safe, ladder, module_plan}`;
  `furniture[].size_snap = {drawn: [w, d, h], snapped: [w, d, h], product, reason}` (T1; `adjusted_by_ai`);
  `furniture[].drawn_group = {anchor_id, members, moved_m}` (T3); `furniture[].type_method` gets the values
  `twin | level | block | group_member` (T3); `site.hedges[]` (T6, see §13.2); `site.platforms[]` (T6).
- Catalogue entries (T1 adds the fields to the existing entries by script; T7 writes them for new entries):
  `licence`, `licence_url`, `licence_declared_by` (`publisher | uploader`), `licence_flag`, `commercial_safe`,
  `attribution`; the existing `licence_flag: null` becomes `"none"`; the 196 TRELLIS.2 entries get `tool_nc`.
- Settings: `brief.library.licence_mode` in `wenart/defaults.yaml` = `commercial` (the product default);
  `projects/real02|real03|real04/brief.yaml` set `library: {licence_mode: relaxed}` (D1, this milestone); the pod
  jobs also export `WENART_LICENCE_MODE` (lead, `scripts/jobs/full.sh`). A flip back to `commercial` reruns fit →
  layout completion → build → render; the volume is untouched.
- Scene manifest: cameras carry `source: searched | replayed` (T5); objects keep `wenart_id` ↔ `asset_id`.
- Final report JSON: `views[].commercial_safe`, `below_library: [{id, type, method, builder}]` (T8).
- A/B levers (T5, T6): `scripts/jobs/levers_ab.sh` renders 8 fixed interior views × variants
  (`WENART_LIGHT_VARIANT`: `sun100 | sun300 | sun1000`, `evcap`, `rig`, `shell`), `scripts/jobs/site_ab.sh` 3
  exterior views × (hedge, instances, sapling, platforms, pools, sky); both write `results/ab_m13/<variant>/` with
  the render manifest, previews, time and VRAM per view. The lead's `scripts/jobs/m13_p1.sh` runs both and the GPU
  tests.

### 13.4 What stays as it is (not in scope of any track)

Camera policy (18 / 16 mm at 1.25 m, D8), AI polish (off, D10), the ingest of walls and openings, levels, the
recognition stage, the gate, the pod runner's limits, the agent model (Qwen3.8-27B-FP8) and its serving.

### 13.5 Order of integration

T1 and T3 first (the fit and the solver feed everything), then T2 and T4, then T5, T6, T8, then T7 (its CPU part;
the downloads run in P2). Each track delivers a report (what was built, tests added, numbers, open items, changes
it needs in other tracks' files). The lead integrates, runs `pytest -m "not gpu"` (4,885 tests on 12 Oct 2026),
commits, pushes, then writes `tests/test_m13_contracts.py`.

### 13.6 Pods (approved under D6; each `--over-5-ok`; one at a time; logged in `docs/gpu-log.md`)

| Pod | Job | Needs first |
|---|---|---|
| P1 | `scripts/jobs/m13_p1.sh`: levers A/B (T5, T6) + GPU tests of T2, T5, T6 | CPU suite green; T5, T6 merged |
| P2 | `scripts/jobs/library_growth.sh` with `ingest-hssd` + `demands` + `size-grid` + audit + gaps | **the user has accepted the HSSD terms on Hugging Face with the account behind the pod's `hf_token`**; T7 merged |
| ~~B0~~ | cancelled by the user on 12 Oct 2026: the committed M11 runs are the baseline of real02 and real03 (the M12 run for real04) | – |
| P3 | full run real04 with the new catalogue (cameras searched: no camera records are committed for real04) | P1 constants applied, P2 catalogue |
| P4 | full runs real02 + real03 with `--cameras-from` the committed M11 scene manifests (set 1) and the searched cameras (set 2) | P3 fixes |
| P5 | one fix round + metric renders | P4 |

## 14. Build log (step 2)

Round 2 (commit aafd636) wired the cross-track asks of round 1 (14.5 lists them) and round 3 applies the pod P1
decisions of 14.3.

Round 1 of the build (commit e1532a8, 15 Oct 2026; the 12 Oct attempt was cut by a usage limit) built the eight
tracks of §13.1 on disjoint files, reviewed them and integrated them. The commit touches 141 files (108 modified,
33 new; +78,945 / -2,684 lines, of which results/library/growth 12 files +52,351, catalogue and size-table JSON
3 files +5,412 / -1,568, wenart code 76 files +14,471 / -950, tests 46 files +5,895 / -159, scripts 4 files +816).
Every number below is marked **[CPU]** (measured here on the committed files of commits 93aff07 real02/real03 and
eddde01 real04, no GPU) or **[pod]** (waits for P1-P5). Pod B0a (12 Oct, the cancelled M12 baseline) ran 4 min for
$0.19 (`docs/gpu-log.md`).

### 14.1 What was built per track

| Track | Built (round 1) | Constants chosen (source) | Tests added | GPU-only, untested here |
|---|---|---|---|---|
| T1 fit and licence | `catalog.py` licence model (`LICENCE_MODES`, `LICENCE_FLAGS`, `licence_mode` env > brief > commercial, `licence_flag_of`, `commercial_safe`, `usable(entry, mode)`, `unusable_reason`); catalogue licence fields by the idempotent script `python -m wenart.furniture licence-fields`; `fit.py` ladder library → module → parametric with `asset.method | ladder | licence | licence_flag | commercial_safe`, `piece.library_gap`, `method none` only for `build: false`; rank without the wood re-sort (generated last > known units > real-size step + diversity penalty > real product > design preference > audit vision quality > texture maps > judge quality > faces > aspect > source > id); one uniform scale to the drawn width (`asset.depth_abs_m` for the layout); pins skip the style filter; diversity penalty per room and project; fabric colour on `asset.fabric_colour`; size snap `sizes.snap_size` / `PRODUCT_GRID` (12 types, 78 cited catalogue ids); `project.licence_mode` written; CLI `fit --licence-mode / --project` | `NON_UNIFORM_CAP` 1.10, `UNIFORM_RANGE` 0.85-1.20, `HEIGHT_TOLERANCE` 0.15, relaxed step 1b `RELAXED_CAP` 1.15 / `RELAXED_RANGE` 0.75-1.30 (the M11 values); `ROOM_REUSE_MAX` 2, `ROOM_REUSE_STEPS` 4, `PROJECT_REUSE_STEP` 1, `SIZE_BUCKET` 0.05, `FACES_LOW` 3000 (the audit's threshold), `VISION_QUALITY_DEFAULT` 3.0, `SNAP_TOLERANCE` 0.05 (one rank step), `ORIENTATION_RATIO` 0.25, `SQUARE_EPS` 0.03; `tool_nc` reason: nvdiffrast v0.4.0 LICENSE.txt §3.3; TRELLIS.2 `licence_url` = its MIT LICENSE page; Poly Haven CC0 (polyhaven.com/license); CC deed URLs from `wenart/assets/objaverse.yaml` (creativecommons.org is blocked) | `tests/test_m13_fit.py` 22 passed (675 lines); T1 batch 123 passed, 1 skipped | none |
| T2 modules and families v2 | new `wenart/blender/modules.py` (957 lines: `module_plan`, `MODULE_BUILDERS` wardrobe / table_dining / sofa_corner / kitchen_counter / kitchen_island / washbasin / shower, `build_module` with one material slot per part key and the Bevel modifier); `parametric.py` families v2 (`FAMILY_TYPES` bed / bed_single / bed_double, sofa, armchair, table_dining, table_coffee, desk, nightstand, dresser, bookshelf, tv_unit, wardrobe; ≥ 2 material slots, bevel radii, 1 mm `FRONT_GAP`); bed v2 platform bed keeping the M4 camera-profile box; `furniture.py` dispatch on `asset.method == "module"`; `textiles.py` re-exports | wardrobe frames 0.50 / 0.75 / 1.00 wide, 0.35 / 0.58 deep, 2.01 / 2.36 high, fillers ≤ 0.13 (IKEA PAX via the GitHub mirror felixrinker/floor-planner @408e3d7c, read 12 Oct; 404 on 15 Oct, ikea.com blocked); kitchen base widths 0.30 / 0.40 / 0.45 / 0.60 / 0.80 / 0.90, depth 0.60, worktop 0.90, plinth 0.10, wall units 0.35 deep (METOD mirror 12 Oct + utariga kitchen rules re-read 15 Oct); sofa modules 0.90-1.10, chaise 0.85-1.00 × 1.60-1.80 (contract + `size_table.yaml`); bath trays 0.80-1.20, vanity depth 0.45-0.60, basin 0.50 × 0.36 (`size_table.yaml`); bed rail 0.03 + gap 0.03 (Movian Loue 160 × 200 in a 1.72 × 2.06 frame); Blender 5.2 `BevelModifier` fields verified on docs.blender.org | `tests/test_m13_modules.py` 14 CPU tests (478 lines); size sweep 105 family cases + 23 module plans: 0 degenerate faces, boxes = plan within 1 cm | `tests/gpu/test_m13_modules.py` 3 tests (slots ≥ 2, Bevel WEIGHT, bounds = plan within 1.1 cm, manifest `by_method.module`) |
| T3 placement | `infer.type_by_code` (twin / level / block / group_member), `code_types` in rounds, step 0 of `infer_types`, a validated type proposal before the solver in `complete_building`; `groups.drawn_groups`, `GROUP_MEMBER_MOVE_MAX_M`; `program.room_program` marks a drawn group `resolve` (anchor missing, misread or failing the checks); `solve_room(..., drawn_group=)` re-solves within 0.5 m; unbuilt anchor no obstacle; F8 names the anchor (`cause: anchor_not_built`); F2 on unbuilt drawn pieces; room aliases, tiers, designer terms R3 / R6 / R12-R14 and the rug member as data in `groups.yaml`; S2 by class | `GROUP_MEMBER_MOVE_MAX_M` 0.5 (D5); `SAME_FOOTPRINT_M` 0.01, `SAME_CENTRE_M` 0.02 (`ingest.twins.TOL`), `CONF_TWIN` 0.8, `CONF_BLOCK` 0.7, `CONF_GROUP` 0.6, `BLOCK_SIZE_TOL` 0.40, `CODE_ROUNDS` 3; `TOLERANCES` overlap_fixture 0.03 / overlap_soft 0.05; tiers small_kitchen < 7 m² (aisle 0.90 soft, walkways 0.60), drawn_run < 14 m² (ours + NKBA + Turkish imar, flagged); small_rooms living 12 m², bedroom 10 m²; R3 2.4-3.0 m / 45°, R6 rug inset 0.30 / dining margin 0.60 / bed runner 0.80, R12 0.80 m, R13 5° / 0.10 m (design books / Merrell 2011 as secondary sources, flagged); weights conversation 1.0, rug 0.5, anchored 1.0, alignment 0.5; `RESOLVE_OVERLAP_M2` 0.05, `RESOLVE_OUTSIDE_M2` 0.02 | `tests/test_m13_placement.py` 24 new (23 fail on the old code, 1 skipped without results/), 3 updated; T3 set 266 passed | none |
| T4 agent loop | new `wenart/agent/causes.py` (342 lines): `accept_edit`, `findings_removed`, `cause_of`, `tools_for_finding`, `BUILDING_WIDE_TOOLS`; the loop runs the dry re-check, carries scene / view / vision findings on a changed target to the next round, logs rejected edits with both finding lists, reports findings removed; building-wide tools only in the building session (refused at call time); idempotent `set_exterior`; `edit_ops.retype_piece` refits through `fit.fit_piece` in `project.licence_mode`, `place_group` through `drawn_groups` + `solve_room(drawn_group=)`, `swap_model` refuses S2 < 0.03 m; room brief with licence mode, drawn groups and below-library pieces; planner rule 7; B5 storeys fix | `MAX_ROUNDS` 3 (the code had 4, the real04 pod ran 6); `S2_SWAP_MIN_M` 0.03 = `TOLERANCES["overlap_fixture"]`; temperature 0 and the strict schemas unchanged | `tests/test_m13_agent.py` 38 items (24 functions + 14 parametrized; 537 lines), 7 test files updated; 191 passed + 1 failed (`AGENT_CODE`, fixed in the integration) | none (pod numbers come from P3 / P4 `metrics.json findings_removed`) |
| T5 light, materials, render, replay | `lighting.py` `SUN_STRENGTH_WM2`, `WENART_LIGHT_VARIANT` base / sun100 / sun300 / sun1000 / evcap / rig / shell / all, fill-light ratio scaled by sun / 3.0, `room_rig` / `rig_plan` / `build_room_rig` (emissive fixtures); `materials.py` `exterior_world_nodes(..., sun_disc=True, ...)` Nishita sky with disc, `shell_material` 7 slots, `apply_shell_layers` coat / sheen / bevel / AO / imperfection, fabric colour path; `render.py` `EXPOSURE_LIMITS (-2, 3)`, `lighting_dark`, project-locked white balance (`RENDER_CODE_VERSION m13.1`), VRAM per view; `cameras.replay_cameras`, `build.py --cameras-from / --cameras-extra` (env `WENART_CAMERAS_FROM / _EXTRA`); `ab.prepare_m13` + `M13_AB_VIEWS`; `scripts/jobs/levers_ab.sh` 8 + 8 fixed views × 8 variants = 128 renders at 128 spp | `SUN_STRENGTH_WM2` 3.0 (M11 placeholder until P1); variants 100 / 300 / 1000 W/m² (Blender 5.2 manual: clear sky 1000, cloudy 500, overcast 200); `SUN_REFERENCE_MOOD_WM2` 3.0; `ALL_VARIANT_SUN` = sun300; `EXPOSURE_LIMITS` (-2, 3) vs M11 (-2, 8); `lighting_dark` critical at ≥ 2 stops over; `RIG_GAIN` 4.0, `RIG_WARM_K` 2700, lumens → W from the manual table (800 lm 2.1 W … 2500 lm 4.5 W); `sun_size` 0.545° (manual default), `EXTERIOR_SUN_DISC_REFERENCE_WM2` 1000; `LEVER_DEFAULTS` ev_cap on, rig off, shell off (as built; all on since round 3, §14.7); shell slot ids white_plaster_02, marble_01, white_planks_clean, Metal032 (`asset_checks_m10.json`) | `tests/test_m13_light.py` 37 CPU tests (547 lines); row 310 passed / 48 skipped / 1 failed (T2's bed, fixed) | `tests/gpu/test_m13_light.py`: T5 counts 6 GPU tests, the integration report 7 items; the committed file has 2 functions, one over 6 variants (base, sun300, evcap, rig, shell, all) + the sun-disc test = 7 items. Shell layers, rigs, sun-disc world, project WB and VRAM sampling in a real render |
| T6 outdoor and site | `hedge_rows` (in `vegetation.py`, re-exported by `sheets.exterior`; `site_of` writes `site.hedges`); `site.tree_height` by crown class (4 m minimum gone); `climate_of` / `species_for`; new `wenart/blender/vegetation.py` (1,303 lines): `tree_object` (Poly Haven instances near cameras, Sapling through `bpy.ops.curve.tree_add`, leaf-card fallback, never a primitive), `hedge_object` (geometry-nodes leaf cards), `grass_patch`, `SPECIES` 19 entries; `site.platforms`, `platform_parts`, `pool_parts` v2, `pool_materials` v2, `backdrop_faces`, `haze_box`, `site_levers` (`WENART_SITE_VARIANT`); facade kit (`facade_kit`, `KIT`); `copies.site_view` `pitch_for_horizon`; `exterior.build_model` hedges as obstacles, `view_check` `hedge_blocked` / `hedge_over`, `aerial_allowed`, X6; `scripts/pod_setup_vegetation.sh` (188 lines), `scripts/jobs/site_ab.sh` (339) | hedge rule ≥ 5 symbols, r ≤ 0.6 m, pitch ≤ 1.5 × diameter, turns ≤ 60° (§13.2); crown classes of §13.2; hedge height class mid = 1.2 m (assumed); site view pitch 13.29° at 24 mm, horizon at 0.78 of the frame, cap 28°; haze density 0.0009 /m, anisotropy 0.3; backdrop ring 1,800 m out, +25 m; pool coping 0.35 m, lip 0.04 m, depth 1.5 m (assumed); Sapling 0.3.7 top-per-scale table measured in bpy 5.2.2 (e.g. japanese_maple 1.33, white_birch 1.27, callistemon 1.04; a generated tree is post-scaled to the drawn height); Poly Haven heroes verified on the API 15 Oct (island_tree_01 5.03 m / 3.73 M polys, island_tree_02 3.41 m, island_tree_03 2.62 m, tree_small_02 4.65 m, jacaranda_tree 19.83 m, fir_sapling_medium 9.16 m; pine_tree_01 17.4 M and fir_tree_01 7.9 M polys left out); Sapling licence GPL-3.0-or-later per its 0.3.7 manifest (GPL-2.0-or-later in its source headers), called through `bpy.ops` only | `tests/test_m13_site.py` 21 CPU tests (528 lines); the six existing row files updated; real04 built end to end under the bpy 5.2.2 LTS module in 27.3 s CPU | `tests/gpu/test_m13_site.py` 2 tests; Sapling extension install, Poly Haven 2K downloads, ambientCG atlases, the site A/B |
| T7 library growth and audit | `audit/demands.py` (`drawn_demands`, `size_grid`, `coverage`, `demand_gaps`); new `wenart/assets/hssd.py` (542 lines: `SYNSET_TYPES`, `hssd_candidates`, `gate_check`, `download` via `huggingface_hub` 2.0.0 `snapshot_download`, token read from the environment only and scrubbed, `entry_fields`); `growth_entries.hssd_entry`; `growth.py` ABO size-grid picks, `polyhaven_vegetation`, `ambientcg_sets` (22 ids), approvals by rule; audit gates `units_anchor`, `pbr` / `pbr_record`, `material_tags` (m13.1 question), `chaise`, `licence_fields`; `growth_run.py` steps demands / size-grid / speed-probe / ingest hssd, ambientcg, abo --m13, polyhaven --m13 / catalogue / gaps / report; `library_growth.sh`; 12 committed lists under `results/library/growth/`; `fetch.check_licence` fixed for the flag word `none` | hssd/hssd-models revision 208ea6bc (14,270 files, 38.45 GB, card licence cc-by-nc-4.0, gated); hssd/hssd-hab `metadata/fpmodels-with-decomposed.csv` revision 4369cb98 (20,451 rows, `aligned.dims` x, y-up, z); paper arXiv 2306.11290 (title and authors from huggingface.co/papers); ABO S3 listings; Poly Haven API categories (trees 20, plants 57, ground cover 32, grass 4, potted plants 6); ambientCG API ids; `speed_probe.budget_minutes` 60, pick floors 600 / 400; M12 download rate 99 MB/s | `tests/test_m13_library.py` 25 tests (676 lines); row tests updated | `blender_audit.pbr_info` (bpy), the speed probe, the real downloads, the HSSD gate, the catalogue step on real files, `tests/gpu/test_library.py -k growth_m13` 3 tests |
| T8 attribution, report, metrics | `copy.attribution_text(title, credits, *, mode)` sections 1-4, `TOOLS_AND_GENERATORS`, `project_credits` + `licence_flag` / `commercial_safe` / `licence_url` and an `[asset: id]` suffix, `texture_credits`, `library_attribution`; `final.py` `views[].commercial_safe {safe, flagged, flags, pieces, assets}`, manifest `licence` and `below_library` blocks, the two report sections; `pack3d.licence_notes` into `README_3d.txt`; new `wenart/report/metrics13.py` (1,009 lines, 17 metrics, CLI `python -m wenart.report metrics13`); new `wenart/report/sheets13.py` (174 lines, one before \| after JPEG per camera, CLI) | `PRICE_USD_PER_H` 2.49 (§7 / §8), `S2_DEPTH_M` 0.03, `BARE_WALL_SHARE` 0.5, `EV_HIGH` 5.0, `STRETCH_LIMIT` 0.05, `BLACK_LEVEL` 16/255, `TILE_HEIGHT` 540 px, `CAPTION_HEIGHT` 72 px; licences verified on the cards: Qwen3.8-27B-FP8 and Qwen3-VL-8B-Instruct apache-2.0, TRELLIS.2-4B mit, Z-Image-Turbo apache-2.0, DINOv3 License (gated); Blender GPL (manual licence page), LibreDWG GPL-3.0-or-later, Poly Haven CC0 + "Powered by Poly Haven" (Public-API README), HSSD BibTeX from github.com/3dlg-hcvc/hssd | `tests/test_m13_report.py` 12 tests (626 lines); 2 assertions updated in `tests/test_run_copy.py` | none (metrics and sheets run on the collected results) |

### 14.2 Numbers measured on the committed buildings [CPU]

**T1 catalogue flags** (script run on the HEAD files): `catalog.json` 121 entries, all `none` (Poly Haven CC0).
`catalog_library.json` 1,297 entries (769 furniture + 528 decor): `none` 998, `tool_nc` 281 (every TRELLIS.2
entry: 196 furniture + 85 decor; audit keep 243, fix 15, removed 23), `non_commercial` 12 (7 CC-BY-NC-4.0 + 5
CC-BY-NC-SA-4.0, all audit-removed), `share_alike` 6 (CC-BY-SA-4.0, audit-removed), `no_derivatives` 0; Infinigen 27
`none`; `licence_declared_by` publisher 1,084 / uploader 213; `commercial_safe` true 998 / false 299. §13.3 spoke of
"the 196 TRELLIS.2 entries": the script flags 281 (the 85 decor entries too). File diff: 1,279 `licence_flag`
null → word, 281 `licence_url` '' → the TRELLIS.2 LICENSE page, plus the new keys.

**T1 drawn anchors** (from_documents sofa, sofa_corner, bed_double, table_dining, wardrobe, desk with
`build != false`; "old" = HEAD code + HEAD catalogue; commercial and relaxed give the same anchor counts because the
relaxed-only models are fixtures and generated items):

| Input | Project | Old: library (none) | New: library + module + parametric (none) |
|---|---|---|---|
| building_fitted | real02 | 16 of 30 (14) | 16 + 10 + 4 (0) |
| building_fitted | real03 | 11 of 15 (4) | 13 + 0 + 2 (0) |
| building_fitted | real04 | 14 of 34 (20) | 22 + 10 + 2 (0) |
| building_final | real02 | 18 of 29 (11) | 16 + 9 + 4 (0) |
| building_final | real03 | 11 of 15 (4) | 13 + 0 + 2 (0) |
| building_final | real04 | 11 of 31 (20) | 20 + 10 + 1 (0) |

The real04 "before" differs by definition: §7 says 11 of 35, T1 11 of 31 (building_final) / 14 of 34
(building_fitted), T8's metric 1 12 of 34 (it counts the dresser with `drawn_type` wardrobe). All four are shown;
the metric script's definition is the one §14 keeps for the after-runs.

**T1 built pieces by method** (building_final; library / module / parametric / none): real02 old 147 / – / 60 / 18
→ commercial 149 / 35 / 41 / 0, relaxed 153 / 35 / 37 / 0; real03 old 76 / – / 18 / 22 → commercial 70 / 10 / 36 / 0,
relaxed 84 / 4 / 28 / 0; real04 old 119 / – / 58 / 40 → commercial 144 / 36 / 37 / 0, relaxed 150 / 36 / 31 / 0.
Flagged assets: commercial 0 / 0 / 0 (the test asserts it); relaxed real02 4 assets on 8 pieces, real03 14 / 15,
real04 4 / 10, all `tool_nc` TRELLIS.2 (showers, washing machines, stoves, sinks, shoe cabinets, two japandi sofas).
Relaxed caps (ladder step 1b) used on 8 / 5 / 8 pieces. Size snaps: real02 6, real03 1, real04 32 (4 beds 2.55 × 2.00
→ 1.80 × 2.00, 8 chairs 0.71 × 0.45 → 0.50 × 0.50, 4 armchairs 0.64 × 0.57 → 0.65 × 0.80, …). Distinct library models:
real02 27 → 55 (commercial) / 56 (relaxed), real03 27 → 48 / 61, real04 26 → 46 / 49; top model objaverse_d2785b57
chair 42 / 40 uses → abo_B0857JM2NC 36 / 38 (the dining sets). real02 living room (60 pieces): 36 change model in
both modes (20 chairs → the ABO chair, 5 none → module, 4 none → library after the snap, 7 library → library by the
diversity penalty and tie-breaks).

**T3 typing, groups and G-checks** (`building_final.json`; "after" = code typing + every room marked for a re-solve
solved and the best candidate without hard failures applied):

| | real02 | real03 | real04 |
|---|---|---|---|
| untyped drawn pieces → typed by code | 32 → 4 (twin 2, level 1, group_member 1) | 42 → 0 (no twins, no second level, no furniture words in the xref block names) | 20 → 3 (level 1 bathtub, twin 1 bathtub, group_member 1 table_coffee) |
| drawn groups (with members) | 29 (8) | 19 (8) | 31 (10) |
| unbuilt drawn anchors (`asset.method none`) | 0 | 0 | 20 |
| rooms marked for a re-solve → re-solved (pieces moved) | 4 → 2 (2) | 1 → 0 | 10 → 2 (4) |
| severities before → after | critical 0 / 0, major 96 → 89, minor 23 → 21 | major 100, minor 7, unchanged | major 33 → 34, minor 9 → 8 |
| solve time | 1.6 s | – | 11.8 s (10 rooms) |

G-checks before → after (only the checks the report lists; the rest were not reported): real02 G1 7 / 7, G2 7 / 7,
G3 5 / 5, G4 13 / 7, G5 11 / 8, G6 12 / 12, G7 6 / 6, G8 4 / 4, G9 4 / 4, G10 18 / 18, G11 19 / 19, G12 5 / 5,
G13 6 / 6, G14 2 / 2; real03 unchanged G1 5, G2 5, G3 3, G4 9, G5 10, G10 29, G11 12, G12 15, G13 5, G14 14; real04
unchanged per check G1 4, G2 4, G5 2, G7 1, G8 3, G9 6, G10 18, G12 4. The counts barely move because the committed
buildings carry the agent's edits and the re-solves need built anchors (the 20 unbuilt real04 anchors are T1/T2
ladder cases); the real before/after is P3 / P4 **[pod]**.

**T4 replay of the committed agent logs through `accept_edit`** (before = the findings of the edit's round, after =
the next round's findings of the same run; record-only tools never go through the acceptance):

| Project (log) | accepted edits | measurable | accepted now | rejected | findings removed | by tool (accepted / rejected) |
|---|---|---|---|---|---|---|
| real02 (M11, three runs) | 50 (3 record-only, 12 in a last round) | 35 | 21 (60 %) | 14 | 21 | move_piece 8 / 6, remove_piece 8 / 1, resize 2 / 0, rotate 1 / 4, change_type 1 / 1, swap 1 / 1, set_room_type 0 / 1 |
| real03 (M11, two runs) | 16 | 15 | 12 (80 %) | 3 (F5, F4, F7 still there) | 12 | remove_piece 8 / 0, move_piece 3 / 2, rotate 1 / 0, resize 0 / 1 |
| real04 (M12) | 183 (13 report_library_gap record-only, 1 last-round set_terrain) | 169 | 15 strict (9 %: swap_model 8, move_piece 4, mark_not_furniture 2, set_camera 1); 19 when the new-critical condition is judged per edit (round 4 → 5 carried 29 X2 criticals from the roof flip) | 154: target still there S2 39, F8 24, F9 17, F3 12, NR 7, G10 6; no target finding 22 (17 set_exterior, 5 remove_piece); F9 not among the round's findings 8 | 15 (19) | – |

Three sources give three real04 numbers: §1.5 / §7 estimated 20 of 160, T4's replay 15 (19) of 169 and
`metrics.findings_removed` on the committed log 20 of 183 (asserted by a test), T8's metric 7 28 of 160 (18 %). They
use different edit sets and rules (last-round edits, record-only tools, the per-edit critical test); the metric
script's rule is fixed for the after-runs. The same for real02 (T4 21 of 35 = 60 %; T8 12 of 41 = 29 %) and real03
(T4 12 of 15 = 80 %; T8 12 of 16 = 75 %).

**T6 hedges, trees, platforms, cameras** (real04 sheets.json of eddde01; real02 building_final): real04 has 101
drawn tree symbols, all r 0.359 m (100 decor entries, 1 duplicate merged by `to_building`); `hedge_rows` finds 4
hedges from 81 symbols (hedge_001 36 symbols 25.5 m, hedge_002 31 / 21.7 m, hedge_003 7 / 4.8 m, hedge_004 7 / 4.8 m;
pitch 0.73-0.80 m; height class mid 1.2 m; species cherry_laurel inferred from the Mediterranean climate read from
the Turkish labels); 20 symbols (19 decor entries) in 2-3-symbol stubs stay single shrubs 0.862 m high (oleander
inferred). §7 expected 2 hedges; the detector finds 4 (two long rows plus the two 7-symbol stubs). Trees per size
class: real04 shrub 19 / small 0 / medium 0 / large 0; real02 small 2 (M11 crowns 3.5 m → 5.6 m, olive inferred) + the
inferred boundary hedge (6 segments, boxwood 0.6 m). Platforms real04: terraces sp_001 -3.00 m (mark lm_014,
retaining), sp_002 -1.40 (steps), sp_003 +1.55 (steps), sp_004 -0.20 (retaining); parking spk_001 +0.75 drawn sloped
(marks spread 6 m, draped with kerbs); each pool joins its terrace deck. Cameras: 6 planned (ext_1-5, ext_7; M12
rendered 4, ext_3 / ext_4 were dropped 63-87 % blocked behind the hedge symbols); now ext_3 blocked 19 % (hedge_over
15 %), ext_4 29 % (hedge_blocked 20 %); ext_6 (frontal) still dropped by copy b2. Site view: pitch 13.29° (was 28°),
horizon at 0.78 of the frame (M12: 1.13, above the frame); CPU check render 320 × 180 at 8 spp: ext_7 black share
0.24 % (M12 29.8 %), ext_1 2.1 %, ext_4 1.1 %. Facade kit: real04 reveal 24, gutter 8, downpipe 10, canopy 4,
wall_light 8; real02 24, 4, 8, 2, 4; guard rails 0. Vegetation unit run in bpy 5.2.2: 8 m + 4 m hedge → 2,617 leaf
cards in 0.02 s; Sapling olive 5.6 m in 0.91 s (14,829 leaf faces); grass 275 m² at 4 / m² → 1,100 clumps.

**T7 drawn demands and coverage** (`results/library/growth/`, 15 Oct): 809 demanded pieces (388 drawn + 421
completion-added; real02 298, real03 222, real04 289) in 156 (type, 1 cm size) rows of 48 types (33 furniture, 15
decor); 90 demanded size bins (75 furniture, 15 decor). Largest: chair 94 (84 drawn), nightstand 36, floor_lamp 30,
toilet 28, bed_double 23 (1.60 × 2.00 n = 20), wardrobe 22, washbasin 21, console_table 20, armchair / ottoman / stove /
table_dining 18, bathtub 17, sink_kitchen 16, sofa 15, shower 14, desk 12. Coverage (≥ 2 usable models per bin
within the fit caps): commercial 53 of 90 bins (furniture 45 of 75), relaxed 60 of 90 (51 of 75); 37 gap rows; 20
bins with 0 models in both modes (bathtub 1.70 × 0.75 and 1.80 × 0.80, kitchen_island 1.20 × 0.80 and 2.00 × 1.00,
shoe_cabinet 0.80 × 0.30, shower 0.80 × 0.80, sink_kitchen 0.60 × 0.50 and 0.80 × 0.50, table_coffee 0.80 × 0.50,
table_dining 2.40 × 1.00 and 3.00 × 1.00, tall_cabinet 0.60 × 0.60, washbasin 0.50 × 0.40 and 0.80 × 0.50; decor basket,
blind, curtain, pendant_light, plant, throw). Relaxed-only coverage: washing_machine 15 (commercial 0), stove
0.90 × 0.60 8 (0), toilet 8 (1), fridge 6 (0), shower 1.00 × 0.80 5 (0) and 1.20 × 0.80 2 (0), plant_large 6 (0).
Pick plan for P2 **[pod]**: HSSD 874 picks (796 furniture + 78 decor; 708 inside the fit caps) 2,466.8 MB; ABO 562
(379 size grid + 120 decor + 33 style + 30 headboards) 12,526.5 MB; Poly Haven 48 at 2K (T7 lists 16 trees / shrubs, 4
grass, 20 ground cover, 8 plants, 3 planter boxes, 1 furniture, which sum to 52, so some picks must sit in two
categories: to confirm) 2,828 MB plus the 88 M12 models re-fetched at 2K; ambientCG 20 of 22 sets 359.6 MB;
about 18.2 GB in all (≈ 3 min at the M12 rate 99 MB/s, 61 min at the probe floor 5 MB/s). Gate dry run over the
current catalogue (1,418 entries = T1's 1,297 + 121): `units_anchor` would remove 197 anchors of guessed units (152
TRELLIS.2 + 45 Objaverse; P2 applies the gate to the new ids only), `material_tags` review 701, `chaise` warn 1 of 28
corner sofas, `licence_fields` ok 1,418, `pbr` skip 1,418 (needs the pod measurement). HSSD listing: 14,270 files,
14,267 GLBs (14,099 objects + 168 stages), 38.45 GB; 10,169 metadata rows typed by `SYNSET_TYPES`, 8,442 of them in
hssd-models.

**T8 baseline of the 17 metrics of §7** (`wenart.report.metrics13` on the committed results: real02 and real03 =
the M11 runs of 93aff07, real04 = the M12 run of eddde01, which has no scene or render manifest → "no data"):

| # | Metric | real02 | real03 | real04 |
|---|---|---|---|---|
| 1 | drawn anchors built | 29 of 30 (97 %) | 15 of 15 (100 %) | 12 of 34 (35 %) |
| 2 | drawn pieces in the scene | 185 of 210 (88 %) | 130 of 165 (79 %) | 128 of 240 (53 %) |
| 3 | `asset.method none` | 0 | 0 | 43 |
| 4 | parametric share of built (of fitted); grey boxes | 109 of 257 (42 %), 132 of 282 (47 %); 21 | 70 of 158 (44 %), 104 of 193 (54 %); 42 | 58 of 177 (33 %), 115 of 289 (40 %); no data |
| 5 | complete group sets | bathroom 10/10, bedroom 6/6, kitchen 0/4, living 2/3 (78.3 %) | bathroom 0/8, bedroom 2/9, living 0/8 (8.0 %) | bathroom 8/10, bedroom 4/8, kitchen 0/2, living 0/4 (50.0 %) |
| 6 | last-round findings F8 / S2 > 3 cm / G10 / LG | round 4: 5 / 0 / 0 / 0 | round 5: 0 / 0 / 0 / 0 | round 7: 38 / 1 (S2 all 17) / 18 / 66 |
| 7 | accepted edits whose finding is gone next round | 12 of 41 (29 %), 50 accepted | 12 of 16 (75 %), 16 accepted | 28 of 160 (18 %), 183 accepted |
| 8 | library pieces: top share; distinct; units unknown; stretch > 5 %; quality ≤ 3 | 28 % (42 of 148); 30; 51 %; 53 %; 4 % | 11 % (10 of 88); 33; 40 %; 38 %; 32 % | 34 % (40 of 119); 26; 50 %; 49 %; 12 % |
| 9 | interior views at EV ≥ +5; EV median gap | 9 of 35; 6.92 EV | 27 of 83; 5.17 EV | 9 of 44; no data |
| 10 | shell slots with normal + roughness; fabric colour applied | no data; 0 of 23 | no data; 0 of 11 | no data; no data (14 upholstered built) |
| 11 | trees built; hedges; black pixels in the site view | 0 drawn; 1 hedge object of 0 drawn rows; 0.0 % (ext_5) | 0 drawn; 0; no data | no data of 100 drawn; no data; 29.8 % (ext_7) |
| 12 | exterior views rendered of planned | 6 of 6 | 0 of 0 | 4 of no data |
| 13 | views in halls or ≥ 50 % bare wall | 16 of 41 (halls 9, bare 11) | 29 of 83 (21, 14) | 12 of 48 (halls 12, bare no data) |
| 14 | `in_json_not_rendered` | 0 | 2 in 2 views | 18 in 10 views |
| 15 | rubric (results/review/m13_step0) | mean 1.90 over 41; 8 at 1; 0 at 4-5 | mean 1.83 over 83; 28 at 1; 1 at 4-5 | mean 1.88 over 48; 20 at 1; 3 at 4-5 |
| 16 | commercial-safe line present; flagged ids missing in ATTRIBUTION | 0 of 41; 0 | 0 of 83; 0 | 0 of 48; 0 |
| 17 | minutes and USD (stage seconds at $2.49/h) | 29 min, $1.22 | 56 min, $2.32 | 122 min, $5.07 |

Where the script's number differs from the §7 column (real04): metric 1 12 of 34 vs 11 of 35; metric 7 28 of 160
vs 20 of 160 (§7 used an unwritten rule); metric 8 quality ≤ 3 12 % vs 52 % (the script counts a lower M8 judge
score ≤ 3 or a catalogue `vision_doubt`); metric 9 gap "no data" vs 7.2 EV; metric 11 29.8 % vs 29 %; metric 12
"4 of no data" vs 4 of 7; metric 17 122 min / $5.07 as the stage sum (it includes the failed 29-min build) vs 114
min / $4.72 pod wall time in `docs/gpu-log.md`. Metrics 10 and 11 need the manifest records T5 (`materials[].maps`,
`recolour.fabric`) and T6 (`site.vegetation`, `site.hedges`) write; until then they read "no data" **[pod]**.
Other T8 measurements: the per-view commercial-safe check on the committed real02 manifests flags 6 of 41 views (3
`tool_nc` generated models), 35 safe; `below_library` 109 pieces, 53 gaps (56 by design); `project_credits` real02
75 models, 66 commercial-safe, 9 `tool_nc`; `sheets13` on real02 41 sheets of 72-170 KB (≤ 300 KB).

### 14.3 Pod P1 (15 Oct 2026): lever A/B, site A/B, GPU tests, and the lead's decisions

Pod `ker0qemve1rhpf`, RTX 4090 ($0.89/h), 163 min, $2.42, round-1 code (33d12db). The lever A/B rendered the 8 fixed
Milestone 11 views of real02 and real03 × 8 light variants (128 spp, 4.4-9.2 s per view on the 4090, 13.5 GB VRAM);
the site A/B rendered 3 exterior views of real04 and real02 × 8 site variants (2-4 s per view, 12.4-13.4 GB). The
vegetation setup worked (Sapling Tree Gen installed from extensions.blender.org and registered; 11 Poly Haven CC0
models, 753 MB; 4 ambientCG atlases). Contact sheets: `results/review/m13_p1/levers/` and `site/` (downsized), the
summaries beside them. GPU tests: T2 modules 3 passed; T5 light 6 passed, 1 failed (the sun-disc measurement script
exits non-zero, so `SUN_DISC_RATIO` was not measured); T6 site 1 passed, 1 failed (`build_site` raises
`KeyError: 'sides'` on the test's planar terrain record; the A/B builds themselves ran).

What the images and numbers show (lead's reading, the sheets are the evidence):

| Lever | Observation | Decision |
|---|---|---|
| sun 3 W/m² (base = M11) | rooms without direct sun are lifted +6 to +9 EV (real02 kitchen metered 9.2 EV): flat, washed out, blue; the replay matches the M11 baseline frame for frame | replaced |
| sun100 / sun300 / sun1000 | a real sun patch through the window, clean contrast, warm; metered EV falls to 2.5-4.3 (sun1000) in rooms with windows; sun1000 reads most natural, no clipping seen | **`SUN_STRENGTH_WM2 = 1000`** (the manual's clear-sky value), the same constant outdoors |
| evcap (+3) alone | a room without light becomes black (kitchen capped from 9.2 to 3.0): the cap is a finding, not a fix | **on**, together with the rig; a capped view is a `lighting_dark` finding routed to the lighting tools |
| rig (fixtures, gain 4.0) | the kitchen strip and pendant turn the +9 EV room into +1.0 EV (a lit kitchen); but the bedside lamp and shades blow out white, and the project white balance, metered on the rig-lit bathroom (3,422 K), turns every daylight view blue-grey | **on** with `RIG_GAIN = 2.0`; the visible shade emission decoupled from the lamp power (shades never clip at the project EV); the project white point metered on daylight only (rig lights hidden in the metering pass; 5,408 K on real02) |
| shell | ceiling plaster, worktops, fronts and tiles differ little at 1080p; no harm; +35 % render time (6.4 vs 4.8 s) | **on** |
| all (sun300 + rig + shell + evcap) | the kitchen and bath look lit and real; the salon and bedrooms suffer the white-balance cast and the blown shades | fixed by the two rig changes above; re-rendered in P3/P4 |
| sky (Nishita with sun disc) outdoors | the sky brightens but the facades stay flat and bluish because the exterior sun lamp is still 3 W/m² (no shadows) | sun 1000 outdoors; the sun disc visible for camera rays only (Light Path mix of the two sky textures) so the lamp is the only sun light; the ratio test fixed and re-run in P3 |
| hedge | the leaf-card hedge reads as a box of yellow-green dots | on; denser cards, atlas alpha and colour from the leaf texture, darker green |
| instances (Poly Haven trees) | the olive instance in real02 ext_1 looks real; the clear win of the site A/B | **on** |
| sapling | the Sapling tree renders without leaves (bare branches) | on only with leaves (the add-on's leaf settings and the leaf atlas material); fallback to leaf-card trees until then |
| platforms | terraces and paths appear, but a retaining wall shows as a tall white box in real04 ext_1 (a platform far above the terrain) | on; retaining height capped (1.2 m, higher differences become stepped terraces), a concrete or stone material, never the facade white |
| pools | coping and water read well in the site view | **on** |
| horizon / haze (all) | the site view keeps the horizon above the lower third; the haze blends the backdrop | on |

Numbers: exterior views cost 2-4 s and ≤ 13.4 GB VRAM with every lever on (the Poly Haven instances add ~0.3 GB);
interior views 4.4-9.2 s. The levers are applied in build round 3 (§14.5) and verified on P3 (real04) and P4
(real02 + real03).

#### 14.3.1 The settings list (T5's list at e1532a8, decided in 14.3)

P1 (pod ker0qemve1rhpf, RTX 4090 at $0.89/h, 163 min, $2.42, on 33d12db) rendered the 8 + 8 fixed interior
views × 8 light variants (128 renders at 128 spp), the 3 + 3 exterior views × 8 site variants, and runs the GPU
tests of T2 / T5 / T6. From its results the lead sets, in T5's own list:

| Setting (file at e1532a8) | Today | Decide from P1 |
|---|---|---|
| `SUN_STRENGTH_WM2` (`wenart/blender/lighting.py` l. 94) | 3.0 (M11) | 100 / 300 / 1000 from the sun100 / sun300 / sun1000 renders against the EV targets of §7 metric 9 |
| `LEVER_DEFAULTS` rig / shell (`lighting.py` l. 107) | ev_cap True, rig False, shell False (all True since round 3, §14.7) | True once the rig and shell variants pass the look; needs the bpy-bound tests `tests/test_blender_build.py` (light_r_L0_hol area light), `tests/test_look_m6.py` (light and tile group links) and `tests/test_blender_materials.py` (material names) updated, because they pin the M6-M12 lights and materials |
| `RIG_GAIN` (`lighting.py` l. 472) | 4.0 | 1.0 if the rig variant is too bright |
| `EXTERIOR_SUN_DISC_REFERENCE_WM2` (`lighting.py` l. 997) | 1000.0 (assumes a Nishita disc at intensity 1 = a 1000 W/m² sun lamp) | the measured `SUN_DISC_RATIO` printed by `tests/gpu/test_m13_light.py::test_exterior_sky_carries_a_visible_sun_disc` |
| `ALL_VARIANT_SUN` | sun300 | whether `all` keeps 300 |
| site levers (`WENART_SITE_VARIANT` all / base / hedge / instances / sapling / platforms / pools / sky, T6) | variants built, no default decided | go / no-go per lever from `scripts/jobs/site_ab.sh` (seconds, EV, VRAM per view, black share) |

The T5 lever and T6 site variants, the 8 + 8 view list (`M13_AB_VIEWS` in `wenart/run/ab.py`) and the GPU tests of
T2 (3), T5 (7 items), T6 (2) are the P1 deliverables; `tests/gpu/test_library.py -k growth_m13` (3) belongs to P2.

### 14.6 Pod P2 (15 Oct 2026): library growth by demand and the audit

Pod `kxvgpycujng0i3`, RTX PRO 6000 ($2.49/h), 46 min, $1.90 (planned 3.5 h: the HSSD step was skipped and the
downloads ran at the M12 rate). The first attempt found no H100 at creation time (the RTX PRO 6000 was out of stock
for an hour) and cost nothing. Code: commit aafd636 (rounds 1 and 2).

| Step | Result |
|---|---|
| demands, size grid, speed probe | 90 demand bins; 14.4 MB/s on the probe (the picks stay at the full lists) |
| ABO (M12 list + the M13 size grid) | 232 + 562 downloaded (12.5 GB); 734 catalogued, 60 dropped (headboards wait for a bed-frame type; copies; outdoor pieces) |
| Poly Haven (M12 at 2K + the M13 vegetation and furniture) | 87 of 88 and 134 of 135 (`decorative_book_set_01` has no 2K glTF on the API); the step counts one failure as rc 1 |
| ambientCG shell sets | 18 of 20 (two API answers arrived cut: `Metal051A` at 60 KiB, `Tiles074` at 1.1 MB: a retry is the fix, round 4) |
| **HSSD** | **0 of 874: the Hub answers HTTP 403 to the token (the token itself is accepted: not 401). The account behind the RunPod secret `hf_token` has not accepted the terms at `https://huggingface.co/datasets/hssd/hssd-models`. The step is skipped by design (D2); the 874 picks and the pattern `objects/*/<id>.glb` match the repo (checked from here on 15 Oct: `objects/0`…`objects/x`, 863 files under `objects/0`).** |
| audit (render, code checks, one vision pass with Qwen3.8-27B-FP8, decisions) | 884 new entries asked (0 failed), 62 second-pass items; written: library 762 keep / 5 fix / 30 removed, Poly Haven 70 fix / 17 removed |
| catalogue copies | 1,950 entries: ABO 1,272 (keep 1,225), generated 308, Objaverse 213, GSO 36, Poly Haven 121; usable commercial 1,519, relaxed 1,777; flags none 1,651, tool_nc 281, non_commercial 12, share_alike 6 |
| coverage after (≥ 2 usable models per demand bin) | commercial 57 of 90 bins (before 53), relaxed 64 (before 60); 33 gap rows, 20 bins still at 0 in both modes (bathtubs, kitchen islands, showers, kitchen sinks, the 3.00 × 1.00 table, the 0.80 × 0.50 coffee table, shoe cabinets, …): every one of them lists HSSD as the source that would fill it |
| preview step, GPU tests | preview rc 1 (no output; round 4); `tests/gpu/test_library.py`: 5 passed, 2 failed (the copies carry Poly Haven at `2k` where the M12 test pins `1k`; an M12 ABO entry without the new `pbr_maps` field in the gates test: both test updates, round 4) |

The copies are now the repo's catalogues (`wenart/furniture/catalog_library.json` 1,181 furniture + 648 decor,
`catalog.json` 93 + 48; the licence fields completed by `python -m wenart.furniture licence-fields`); the models
are on the volume under `/workspace/assets/models/`. The P2 reports are under `results/library/growth/` and the
copies under `results/library/audit/p4/catalogue/`. The 20 empty bins stay library gaps (the fallback ladder
builds them) until the HSSD step runs. **16 Oct 2026: the user has accepted the HSSD terms with the account behind
the RunPod secret `hf_token`.** Pod P2b runs only the HSSD part (`GROWTH_ONLY=hssd`, built in round 3; every other
download and entry stays as it is on the volume), about 30 min; the gate check confirms the acceptance at run time.

**Pod P2b (16 Oct 2026, HSSD layer):** pod `b1ab7tktt9xy2r`, RTX PRO 6000 WK ($2.59/h), 78 min, $3.35, code 47bd941,
`GROWTH_ONLY=hssd`. The gate passed (the user's acceptance reached the token's account): **874 of 874 HSSD objects
downloaded in 244 s**; 852 catalogued (22 dropped), the 884 P2 entries kept unchanged. The audit render took 27 min
and the judge-model setup 32 min, so the vision pass hit the job's deadline: 283 of 853 HSSD models asked (the second
pass of 310 earlier doubtful items finished). Written: HSSD 217 keep, 12 fix, 63 removed, **560 pending** (pending
entries are never used); the republished `vintage_wooden_drawer_01` was re-audited and removed (1.72 m is no drawer).
The audited HSSD models are furniture (chair 33, armchair 32, desk 30, bench 24, bed_double 22, bookshelf 22,
dresser 21, console_table 15, bar_stool 12, bed_single 10, bathtub 5, floor_lamp 3); the fixtures the user accepted
HSSD for (toilets, washbasins, showers, kitchen sinks, stoves, fridges) are among the 560 pending. Catalogue now:
2,681 entries (library 1,955 + decor 726), usable commercial 1,417, relaxed 1,904; demand coverage relaxed 66 of
90 bins (commercial 57). The GPU tests had no time left. **Pod P2c** re-runs the same command with 120 min: the
answers on the volume are reused, so it asks only the 560 left.

**Pod P2c (16 Oct 2026, HSSD audit resume):** pod `kbr2depvz47vu0`, RTX PRO 6000 WK, 52 min, $2.25, exit 0. The 283
answers of P2b were reused; every HSSD model is now audited: **736 keep, 32 fix, 84 removed** (852). Library GPU tests
8 of 8 passed. Catalogue: 2,681 entries, usable commercial 1,417, **relaxed 2,443**; demand coverage relaxed **78 of
90 bins** (66 after P2b, 60 before Milestone 13), commercial 57. Usable HSSD models by type (relaxed): wardrobe 43,
table_dining 41, armchair 36, chair 36, nightstand 35, desk 33, floor_lamp 33, sofa 33, shower 31, bookshelf 27,
bed_double 24, bench 24, table_coffee 24, bathtub 23, dresser 23, ottoman 22, tv_unit 22, sideboard 21, washbasin 21,
stove 18, console_table 16, sink_kitchen 14, sofa_corner 14, washing_machine 11, fridge 10, toilet 9, and more.

**Two fit fixes found by a CPU fit of the three buildings on the grown catalogue** (16 Oct 2026, before P3):

- A not-built piece (`build: false`) searched the library before the not-built rule, so with HSSD a model fitted a
  not-built sofa and would have been credited although nothing is built. Now a not-built piece gets no model and
  its ladder reads "not tried" for every step (unknown pieces keep their parametric record).
- A uniform scale to the drawn width also scales the height: a 2.9 m HSSD dining table scaled 1.155 to a drawn 3.35 m
  stood 0.88 m high (bar height) and passed, because the size table's dining range is 0.65-0.92 m (widened by
  counter-height ABO tables) plus 15 %. Dining tables and desks now keep their working height: within 8 % of the size
  table's product height (`WORKING_HEIGHT_TYPES`, `WORKING_HEIGHT_TOL`); the 3.35 m tables go to the module builder
  (`table_long`, 0.75 m), which keeps the chairs of a deep footprint.

CPU fit of the committed buildings on the final catalogue (`building_fitted.json` refitted; pieces by method):

| Project | Mode | pieces | library | module | parametric | none | HSSD | fixtures from the library |
|---|---|---|---|---|---|---|---|---|
| real04 | commercial | 240 | 114 | 32 | 76 | 18 | 0 | 10 of 48 |
| real04 | relaxed | 240 | 140 | 20 | 62 | 18 | 53 | 34 of 48 |
| real02 | commercial | 210 | 92 | 32 | 86 | 0 | 0 | 10 of 38 |
| real02 | relaxed | 210 | 116 | 20 | 74 | 0 | 41 | 32 of 38 |
| real03 | commercial | 165 | 43 | 10 | 112 | 0 | 0 | 10 of 39 |
| real03 | relaxed | 165 | 64 | 0 | 101 | 0 | 30 | 31 of 39 |

(none = pieces with `build: false`; real04's 12 not-built fixtures are drawn pieces the reading did not type.)

### 14.7 Build round 3 (commit 47bd941, 15-16 Oct 2026): the P1 decisions applied

The round was cut by a usage limit on 15 Oct and resumed on 16 Oct (the finished agents replayed from cache; the
placement agent continued from its partial edits; a library agent was added). CPU suite: **4,988 passed, 0 failed**
(211 skipped without Blender, 139 GPU tests deselected).

| Area | What changed | Constants (evidence) |
|---|---|---|
| Light | sun at the manual's clear-sky value; rig, shell and EV cap on in production; variants `m11` (the before) and `base` (production) for the A/B | `SUN_STRENGTH_WM2` 1000 (P1 sun1000: real02 salon EV 2.5, kitchen 4.3, bedroom 3.2); `RIG_GAIN` 2.0; `LEVER_DEFAULTS` all on |
| Fixture shades | the visible shade is a fixed-radiance emitter, the light inside carries the power | `SHADE_EMISSION_WM2SR` 2.0; measured on bpy 5.2.2: AgX clips at scene-linear 32, so the bound at the +3 cap is 4.0 |
| White balance | one white point per project, metered on daylight only (rig hidden; rooms with windows first); recorded as `white_balance_project` | P1 metered 3,423 K on the rig-lit bath; the daylight point is expected near 5,400 K |
| Exterior sky | the sun disc is visible to the camera only (Light Path mix), so the lamp is the only sun light; the sky's sun now sits at the compass azimuth (the M3-M11 formula put real03's sky sun 30° off its shadows) | measured `SUN_DISC_RATIO` 0.129, mix residual -5e-5 of the lamp (CPU, bpy module) |
| Site | Sapling trees with leaves; hull-shaped hedges with an opaque core and denser cards; retaining walls capped and stepped; concrete or stone edges; lawn tiling, variation and bump; own manifest kinds; site instances realized in the 3D export | `RETAINING_MAX_M` 1.2; `LEAF_ATLAS_OPAQUE` 0.40 (assumed) |
| Placement | uniformly scaled wall-backed pieces planned at their fitted depth; drawn tables split before the size snap; solver rugs survive the decor stage; code typing and the context rules run before the recognition questions | – |
| Library job | complete reads and retries of API answers; Poly Haven size fallback; preview step fixed; `GROWTH_ONLY=hssd` (pod P2b); the drawer re-measured from the republished file (1.715 × 1.007 × 1.091 m, audit pending, re-audited on P2b) | – |

What P3 must look at (open risks, decided after the images):

- `tests/gpu/test_render.py::test_white_plaster_walls_are_neutral` is expected to fail: synthetic-01 measures R/B
  1.186 against the accepted limit 1.12 under the new defaults (2,700 K fixtures under a daylight white point). The
  limit is not changed before the real renders are seen.
- Rooms lit only by the rig (windowless baths and halls) will look warm under the daylight white point; six of the
  16 P1 views are estimated above the +3 cap and become `lighting_dark` findings for the agent's lighting tools.
- Two real04 retaining walls stay above the 1.2 m cap (1.32 m and 1.58 m) because a stepped band would land in the
  draped parking; recorded with the reason in the site manifest.
- Hedge look (the card density follows an assumed atlas opacity), steep-slope kerbs, the real02/03/04 recognition
  question counts after the K3 order (M12: 88 / 95 / 100), and the M6 cushion test (`test_row8_bed_bevel_veneer_and_metal`,
  not caused by round 3).

### 14.8 Pod P3 (real04 full run)

**Attempt 1 (16 Oct 2026):** pod `j66c1kan6qr62r`, RTX PRO 6000 WK, 27 min, $1.15, exit 1 at the layout stage. The
vegetation setup worked (Sapling registered on the new pod), recognition and fit ran; the layout then refused its
own result: the locked check compared the final `drawn_footprint` of the two YATAK beds (`f_L0_007`, `f_L0_008`,
the drawing 2.55 × 2.00 m kept by the round-1 size snap) with the layout's source, the fitted building, where the beds
are already 1.80 × 2.00 m; the drawn-group re-solve had moved them. Fix (`wenart/furniture/locked.py`
`drawn_value`): when an earlier stage changed a drawn piece, its `drawn_*` values are the reference for type,
footprint, front and height; a piece that loses its drawing still fails (test
`test_a_piece_an_earlier_stage_changed_keeps_its_drawing_as_the_reference`, and the P3 beds replayed: two
violations before, none after). A CPU pre-flight of the later stages runs before attempt 2.

**CPU pre-flight (16 Oct 2026, commit 3ed3383):** every stage after the fit was run here on P3's real inputs (real04)
and on real02 and real03 (their committed buildings refitted, relaxed): layout, decor (rule and AI paths), refit and
the agent loop against the repo's fake model server, with the CPU re-run and the locked check after each stage; the
Blender build and a small CPU render through the Blender 5.2.2 Python module. No stage crashed after the fixes; the
locked check passed after every stage on all projects; the 6 real04 solver rugs survive both decor paths; the fit
gives real04 34 of 34 drawn anchors built (M12: 12 of 34).

| Area | Bug found with the real inputs | Fix |
|---|---|---|
| agent edits | open-kitchen zone groups (`<room>_kitchen`) not found by `complete_group` / `move_group` | the group's room read from the group record |
| agent edits | `mark_not_furniture` left the piece in `needs_review`: the dry re-check refused all 20 real04 cases | the piece leaves `needs_review` |
| agent edits | a second edit of a piece dropped the `fix_fixture` allowance: real03 toilets broke the refit's locked check | `adjusted_by_ai` keeps earlier allowances and `drawn_group` |
| agent plan | the default checklist sent `complete_group` to the kitchen id | the group id |
| report | without a scene manifest the report read no building ("commercial", empty below-library list) | the building is read from the run |
| decor | a twin copy of a solver rug kept the source room's group | the twin room's group |
| scene manifest | platform and hedge entries without `parent`: the real04 manifest failed its schema (32 errors) | the parent recorded |
| exposure | the EV floor -2 dated from the 3 W/m² sun: every sunlit view was clamped and rendered near white (real04 ext_7 wanted -7.6 EV) | the floor moves with the sun: -2 − log2(sun / 3 W/m²), -10.4 EV at 1000 W/m²; the cap stays +3 |
| vegetation | a tree that fell back to leaf cards recorded no reason | `fallback_from` and `fallback_reason` |
| materials | the worktop record named `marble_01` although the set was missing | the set is named only when used; a missing set is recorded |
| site meshes | 732 ground and 112 grass faces used a vertex twice (glTF export refused the meshes) | clip points merged before faces are made |
| cameras | replayed records the build did not use were dropped silently | listed with the reason |

Left for round 4 (before attempt 2): the exterior sky world is about 4 stops too dark against the 1000 W/m² lamp
(nearly black at the metered EV, grey only through the haze); the worktop set is never fetched by the assets stage;
nothing reads `lighting_dark`; no v2 chair family (a chair below library level is a one-material box); the agent may
mark drawn fixed equipment as not furniture; the recognition model's whitespace loop (5 of 8 sheet_region answers on
P3).

**Round 4 (16 Oct 2026, commits fe86436 and the follow-up):** the six items above, fixed and tested on CPU.

| Item | Before | Fix | Check |
|---|---|---|---|
| Exterior sky | Nishita world at strength 0.5 against the 1000 W/m² lamp: about 4 stops too dark | `materials.exterior_sky_strength` pairs the sky with the lamp from a measured sun-ratio table (5-85°): 7.71 at 35°; the visible sun disc stays camera-only; the build manifest records `sky_calibration` | diffuse-to-direct 0.166, between pvlib's Bird clear-sky values for AOD500 0.05 and 0.1; real04 ext_7 sky band grey (79, 80, 80) → blue (100, 116, 127) in a CPU render |
| Shell texture sets | worktop `marble_01` and handle `Metal032` never fetched | `fetch.shell_texture_rows(style)` reads the one slot table in `materials.py`; the assets stage fetches them; the build fingerprint lists them (`build.referenced_asset_ids`, read from the same table), so a build cached before a set reached the volume is redone | 98 referenced ids on real04, the 4 shell sets included; `test_referenced_assets_follow_the_shell_sets_the_assets_stage_fetches` |
| lighting_dark | written by the render, read by nobody | a code-critic finding (`critic_code.lighting_items`, family `lighting`), routed to `set_lighting` for interiors and report-only for exteriors; a report section; `set_lighting` is idempotent and capped at x0.5-x3. Follow-up: an edit whose factor stays below what the view needs keeps the finding and is refused (`loop.lighting_kept`, predicted from a trial building with the new factor, not re-rendered); a view that needs more than x3 has the cause `lighting_beyond_cap`: no tool, reported (an edit counts only when its finding is gone) | x2 clears a view that needs x1.82, x1.5 is refused with the prediction; real04's basement salon (about x10) is report-only |
| Chair below library level | a one-material box | parametric chair v2: legs or sled, seat pad at 0.45 m, back panel, 2-3 material slots, bevels; the long-table module builds it | `tests/test_m13_modules.py`, GPU test in `tests/gpu/test_m13_modules.py` |
| Fixed equipment | the agent could mark a drawn kitchen run or WC as not furniture | `mark_not_furniture` refuses fixed types; the acceptance refuses an edit that removes a room's required fixture | `tests/test_m13_agent.py` |
| Recognition whitespace loop | 5 of 8 sheet_region answers were whitespace runs | per-question `max_tokens` and a guard that retries a whitespace-run answer once in compact form (vLLM 0.30.0 has no per-request whitespace option) | `tests/test_recognition_cpu.py`, `tests/test_vllm_schemas.py` |

Review of the follow-up (16 Oct 2026, 15 agents, every finding checked by two more): the first version of the lighting
rule never fired (it read the metrics from a key the real findings do not have; the test built its own shape) and
the set_lighting re-check saw the building without the new factor; both fixed with tests on the production shape.
The same review found that the dry re-check rebuilt the scene, view, look and lighting findings (S1-S6, V1-V3, X6,
L7, R4, R5, X8, lighting_dark) from the round's manifests, which no edit changes: a finding an earlier edit of the
round had removed came back on the next edit as a new one, and a new critical one rejected an unrelated edit. These
findings now come from the round's list (`loop.after_findings`); a fresh collision is still found by the re-measured
checks (F9). A second review (16 agents) found that the set_lighting trial was copied before the tool took the lock
(parallel room sessions could make it stale), that an accepted set_exterior or set_lighting never reached the later
dry re-checks of its round (an accepted roof override's X2 came back as a new critical finding and rejected the
next edits), and that the first accepted set_lighting closed every set_lighting step of its room; all three fixed
with tests that fail on the old code. Checked and not a defect on the real path: a V1 "camera inside a piece" from
the re-check (the render manifests carry no camera positions, so that check never runs there). A third review
(commit 3724033) found an older bug: the loop kept one copy of overrides.json for the whole run, so after the
scheduler rolled back edits a refit refused, the loop's next accepted edit saved the stale copy and the rolled-back
edits came back (`Overrides.reload`, fixed after P3 attempt 2 started; P3 runs without it, P4 with it). Known and kept: the GPU test
`test_white_plaster_walls_are_neutral` is expected to fail (R/B 1.186 against 1.12), the interior HDRI stays
5.2 stops below the clear-sky pair (an A/B lever), and `set_lighting` has no add-lamp tool.

**Attempt 2 (16 Oct 2026):** pod `rjom6ve943tqz0`, RTX PRO 6000, 114 min, $4.73, commit 3724033. Every stage ended
ok (3 agent rounds, build, render, export, check, report); exit 1 came from 4 GPU tests (2 stale pins, 2 real defects).
Results: `results/review/m13_p3/` (48 before | after sheets against M12 eddde01, the 17 metrics, the final report,
the contact sheets). Analysis by 4 analysts, every proposed code fix checked by a second agent.

| # | Metric (§7) | M12 | P3 | Target |
|---|---|---|---|---|
| 1 | drawn anchors built | 12 / 34 | 34 / 34 | 100 % |
| 2 | drawn pieces in the scene | 53 % | 74 % | ≥ 90 % |
| 4 | parametric share of built pieces; grey boxes | 33 % | 10 %; 0 | ≤ 25 %; 0 |
| 5 | rooms with a complete group set | bath 8/10, kitchen 0/2 | bath 10/10, kitchen 2/2 | ≥ 90 % |
| 6 | last-round F8 / S2 > 3 cm / LG | 38 / 1 / 66 | 2 / 10 / 8 | ≤ 5 / ≤ 3 / ≤ 5 |
| 7 | accepted edits whose finding is gone next round | 18 % | 74 % | ≥ 60 % |
| 8 | top model share; distinct models; stretch > 5 % | 34 %; 26; 49 % | 5 %; 97; 0 % | ≤ 15 %; ≥ 60; ≤ 10 % |
| 9 | interior views at EV ≥ +5 | 9 / 44 | 3 / 42 (13 held at the cap) | 0 |
| 11 | trees as real geometry; black pixels in the site view | primitives; 29.8 % | 20 / 20; 6.6 % | 100 %; 0 % |
| 14 | in JSON, not rendered | 18 | 0 | 0 |
| 16 | commercial-safe line; flagged assets missing in ATTRIBUTION | 0 %; – | 100 %; 0 | 100 %; 0 |
| 17 | minutes of stages | 122 | 104 | ≤ 150 |

(Metrics 6 and 7 count this run's events only; `metrics13` read the whole appended log, a bug fixed in the fix round.)

What worked: all 34 drawn anchors built (30 library: 21 ABO, 9 HSSD; 4 module), 91 HSSD pieces from 49 models,
no grey boxes, shell sets 4 of 4 fetched and used, the sky calibration record (7.71, diffuse-to-direct 0.166),
vegetation from real models (hedges, shrubs, 915 grass instances; the M12 lollipop trees are gone), the recognition
guard (5 of 5 whitespace runs answered on the compact retry), every view with its commercial-safe line, ATTRIBUTION
complete. The image of the furnished rooms is clearly better than M12.

What did not: light and colour. 24 of 48 views carry an orange cast (windowless baths, kitchens and halls under the
2700 K rig with the daylight project white point); bedroom r_L0_yatak_odasi_4 renders night-dark (its rig of two
bedside lamps replaced the fill light); the roof-terrace views render under the interior HDRI (black or dusk sky);
interior windows show a blank pale outside (the window pull stops 5-8 stops short); the exterior EV varies by 3.7
stops between views (ext_1/2/4 washed out); ext_5 is an aerial without a horizon. Geometry: a closed door's 5 mm
leaf gap leaks light (GPU depth test, 196 m through the door); the drawn kitchen sinks sit inside the module
counter runs (no cut-out: nothing sets `module_hints`); an unverified extra wall from the second plan region seals a
bedroom alcove with a drawn desk. Agent: one session per round ran out of the 32k context (the final round logged
"the agent model did not answer"); set_lighting gains measured below the linear prediction. Library: a Disney-print
cushion, a mirror-chrome bathtub and a sporting-goods rack as a bookshelf passed the audit. These go to the fix round
(§14.9) before P4.

### 14.9 Fix round after P3 (16-17 Oct 2026; no pod)

Six tracks worked in parallel on the P3 analysis (every proposed fix checked by a second agent; where a verifier
corrected a fix, its better fix was built), then one integration step applied the cross-track asks and ran the full
CPU suite. Nothing here has run on a GPU yet: the GPU checks named below run in P4/P5.

**Agent (track A).**

| P3 problem | Fix | Test |
|---|---|---|
| One planner session per round passed the 32,768-token context; the 400 was retried and logged as "the agent model did not answer" | `loop.ContextBudget` estimates the next prompt; tool results enter the conversation cut at 6,000 characters (was 12,000); when the prompt plus the answer budget pass `max_model_len` − 1024, the results older than the last 2 replies become one-line stubs, then older ones, then the latest are cut to 2,000 characters. A refused prompt (`model.ContextFullError`, never retried) is cut and sent once more; a second refusal ends the session with the new stop `context_full` and a `check` event (tool `context_budget`). `model_error` stays for timeouts, server errors and no connection | `tests/test_agent_loop_p3.py`, `tests/test_agent_model.py` |
| No repetition guard on agent calls; planner answers up to 4,096 tokens | `repetition_detection` on every agent request (as the recognition client); the planner's answer budget is `PLANNER_MAX_TOKENS` = 1536 with thinking off; the call log keeps `finish_reason` and `max_tokens`; a JSON answer stopped for repetition is asked again once on one line; `max_model_len` read from the served key's `--max-model-len` (default 32768) | `tests/test_agent_model.py` |
| "Findings removed" printed the dry re-check's prediction | the stop note, `summary()["findings_removed"]` and the scheduler's note give the measured number (the next round's critics); the dry re-check count is labelled predicted (`findings_removed_predicted`) | `tests/test_agent_loop_p3.py`, `tests/test_run_agent.py` |
| set_lighting gains below the linear prediction | acceptance unchanged (linear); the finding message and `metrics.set_lighting_suggested` suggest min(x3, needed × √2) of headroom | `tests/test_agent_loop_p3.py` |
| The mirror dec_L1_009 through the roof was sent to the building session | decor pieces map to their room; cause `decor_under_roof` has no tool and is reported to the decor stage (`report_to: decor`, `not_yours`); the report lists it (integration) | `tests/test_agent_loop_p3.py` |
| Vision "not a mansard roof" against the built mansard roof | an X2 roof-type claim is dropped when the build makes the drawn type (`critic_vision.drop_roof_type_claims`); an overridden roof keeps the claim | `tests/test_agent_loop_p3.py` |
| `log_seq` off by 1-2 under parallel sessions | `AgentLog.reserve()`: the edit's event takes the reserved seq | `tests/test_agent_loop_p3.py` |

**Light and colour (track L).** `RENDER_CODE_VERSION` m13.2.

| P3 problem | Fix | Check |
|---|---|---|
| Orange cast in 24 of 48 views (2700 K rig under the daylight white point) | each interior view meters twice (rig on, rig hidden); its white point mixes the project anchor and the rig's white point by the rig's share of the light (`render.mixed_whitepoint`; share 0 = anchor, 1 = the rig's own); exterior and open-air views keep the anchor | bpy shim, synthetic-01 wall R/B: bath 1.343 → 1.058, hall 1.80 → 1.29, salon 1.181 unchanged |
| Roof-terrace views under the interior HDRI (black or dusk sky) | open-air rooms (room type `balcony`) render under the exterior world; cameras carry `wenart_room_type` (build passes the room types: integration) | real02 shim: teras_1 under the exterior world, 0 % black sky |
| Exterior EV spread 3.7 stops, washed-out sky | per view a sky pull (depth-pass sky mask, k = 1..4 stops) to sky median ≤ 0.8 and saturation ≥ 0.12; none qualifies (beside the sun) = no pull | real02 shim: ext_2 k = 2, ext_1 no pull |
| Blank pale windows (pull stopped at 1-2 stops) | window pull up to 10 stops to pane p90 ≤ 0.85 or median ≤ 0.65 (schema `window_pull.k` 0..10: integration) | synthetic-01 salon k = 1, p90 0.837 |
| Night-dark windowless bedroom | a rig replaces the fill light only when it has a ceiling fixture (`lighting.rig_replaces_fill`) | real02 shim: r_L0_yatak_odasi_3 gets its fill back |
| Halls and stairs over the EV cap | hall/stair fixtures carry bulbs for 450 lm/m² (the bath density) | predicted +1.8..+2.8 EV (P3 +4.6..+5.1) |

**Geometry (track G).** Door stops on every framed door (Milestone 6 doors via `shell.door_m6_parts`, Milestone 10
doors via `parametric.door_parts`; the stop sits on the leaf face away from the swing, pocket doors on both faces, an
astragal on double and folding doors): P3's 196 m depth through the slit of a closed door is gone (5 of 5 test rays
hit the door in the bpy module; with the old code all 5 pass through). A drawn sink inside a counter run is built into
it (`fit.kitchen_built_ins`, `asset.built_in`, no object of its own; the run's plan lists it under `built_ins`); a
drawn stove stands in a gap of the run (`plan.gaps`: no base unit, plinth or worktop over it). Check S2 now reports a
sink, stove, fridge or washing machine buried in a run (share ≥ 0.25 of its box inside the run's mesh; the committed
real02 "fridge" blocks inside four counters will show as buried). The agent's refit of a run passes the same hints
(integration, `edit_ops._build_retyped`).

**Site (track S).** The aerial ext_5 pitches for the horizon at 0.86 of the frame (15.66° at 26 mm, was 30°: no
sky); the CLAUDE.md horizon rule now also covers the one true aerial. Site finish sets are fetched
(`fetch.site_texture_rows`, from `exterior.build_finish_slugs`; the fetch log prints them: integration): the retaining,
terrace and pool walls get Poly Haven concrete_wall_001 (CC0). The worktop is ambientCG Marble012 (CC0) with a 2 m
repeat (marble_01 reads as tiles); painted trim and fronts are a paint finish without the plank photo. Plants stand on
their terrace (`site.stand_terrain`); hedges keep their hull on their planting side (`site.fit_hedges`, at most 0.5 m,
logged `inferred`). The lawn relief only goes down and keeps the ground's edges. The 100 real04 tree symbols (crown
0.36 m) were checked: they are shrubs by the CLAUDE.md rule. ATTRIBUTION lists Marble012 and concrete_wall_001 when
used.

**Ingest (track I).** A secondary plan page (real04's region r16) adds an extra element only when it neither repeats
nor crosses the master's: the wall that sealed a bedroom bay with its drawn desk is no longer added; doors, wardrobes,
beds and desks drawn twice are not added (listed as `not_added` in the conflict). A secondary page's questions are
never asked and keep no piece waiting; its crops go to their own folder. The camera model treats a wall inside a room
outline as a wall.

**Report and library (track R).** `metrics13` counts the latest run of an appended log only (`run_first_seq`):
corrected P3 numbers m6 38 (round 4) and m7 29 of 39; m2 adds the share without the 38 explained non-furniture pieces
(178 of 202, 88 %). `results/review/m13_p3/metrics13_p3_vs_m12.*` were regenerated (integration). `final/` moves the
previews and plan crops of cameras a run does not have into `final/earlier_run/` (never deleted). The audit gains the
hard title flags `branded` and `other_use` and the `sanitary_finish` check; 7 catalogue entries are removed (the 5 P3
findings plus Holywell Copper and gen_bathtub_industrial_3). Removing 2 cushions and 1 books entry shifts
`fit.pick_index` (sha256 % n) for every cushion and books host in every project, real02 and real03 included.

**Integration (this step).** Applied asks: the decor stage keeps wall decor (picture, mirror, clock) under the sloped
ceiling at its own wall (`decor.wall_art_for_host` reads `ceiling_over`; P3's mirror, 0.80 m of ceiling over its
wall, is left out); the build passes the room types to the cameras and the built-in list into the scene manifest's
furniture summary; the render schema takes the deeper window pull, the sky pull and the new white-point fields; the
run plan counts 4 s per view for the pulls and the second metering pass (was 1 s); the scheduler's agent note names
measured and predicted removals; the agent report lists the findings reported to other stages and the context-budget
events; the log schema documents `finish_reason`, `max_tokens`, `cause`, `not_yours` and `report_to`; the assets
stage prints the site sets; the agent's run refit passes the kitchen hints. New GPU checks: `tests/gpu/test_agent.py`
(repetition stop and call log on the served key, a context-full 400 sent once, the served `max_model_len`) and
`tests/gpu/test_render.py::test_closed_door_views_end_on_the_door` (cam_r_L1_koridor_2_2: depth < 60 m, coverage
≥ 0.9999). Pins updated on purpose: S2 buried sink (`tests/test_scene_checks.py`), the aerial pitch
(`tests/test_blender_exterior.py`), the worktop and front slots (`tests/test_m13_light.py`,
`tests/test_blender_look.py`), the moved stale preview (`tests/test_report.py`), the plan minutes
(`tests/test_run_plan.py`). Not applied: the sun-azimuth penalty for exterior corner views (needs the sun direction
in `plan_exterior`; tracked for P5), unique recognition keys across pages (optional; I's changes make the clash
harmless) and the GLB metallic factor in the audit (optional follow-up). Full CPU suite after the integration
(`pytest -m "not gpu"`): 5147 passed, 212 skipped (no Blender binary), 4 xfailed, 0 failed, 45:54 min.
`tests/test_blender_build.py` through the Blender 5.2.2 Python module: 27 passed; a synthetic-01 L0 build there records
the room type on every camera and the `built_in` list in the furniture summary. Every new test of the integration
(`tests/test_m13_p3_integration.py`) fails on the code without it.

Decisions for the user (from the tracks): the planner's 1536-token answer budget (raise to 2048 if P4/P5 show
`length` stops); `context_full` as its own stop; the lamp-lit halls at bath density instead of the Milestone 12 fill
light; whether open-air rooms drop the invisible fill light; whether P4 runs the interior-HDRI/sun pairing A/B with
the deeper window pull; the stove gaps (revert = drop the `ranges` hints); the S2 buried threshold 0.25; the built-in
sink representation (build true, no object of its own).

GPU checks for P4/P5: `pytest -m gpu tests/gpu/test_agent.py tests/gpu/test_render.py tests/gpu/test_m13_modules.py
tests/gpu/test_m13_light.py tests/gpu/test_m13_site.py tests/gpu/test_look_m6.py` on the real04 run.

### 14.4 Open items and risks by track

- **T1**: uniform scaling leaves a depth mismatch of up to 10-15 % that `furniture.py` centres (a sofa may overhang
  4-7 cm at the back; the back-edge rule and the S2 tolerance are T2/T3's); the 4 real02 desks 1.45 × 0.91 m lose
  their library model (no audited desk deeper than 0.78 m) and go to the parametric desk; the matched-set exemption
  of the diversity penalty may want the user's OK; three real04 snaps deserve a look at the plan crops (armchairs
  0.64 × 0.57 → 0.65 × 0.80, the 0.56 m round "coffee tables", the corridor 1.52 × 0.60 "coffee tables", probably
  consoles); the agent's refits must pass `mode=project.licence_mode` (`fit_piece` defaults to commercial).
- **T2**: PAX / METOD sizes verified only through the 12 Oct mirror (404 and ikea.com blocked on 15 Oct); sofa module
  widths come from the contract and the size table, not a manufacturer's list; 24 types have neither a module
  builder nor a v2 family and keep their M4-M12 look (bar_stool, bathtub, bench, bunk_bed, chair, chaise,
  console_table, crib, display_cabinet, floor_lamp, fridge, office_chair, ottoman, potted_plant, shoe_cabinet,
  side_table, sideboard, sink_kitchen, stair, stove, tall_cabinet, toilet, wall_cabinet, washing_machine); the
  `bevel_weight_edge` attribute name is the one used since M6, not from a page fetched this session.
- **T3**: the decor stage resets `building["decor"]` and drops the solver's rug members (round 2); the ingest still
  asks the AI about footprints code can type (round 2, K3 order); only 2 of 10 marked real04 rooms re-solve on the
  committed building (the others need the built anchors); the designer numbers and the Turkish minimum areas come
  from secondary sources (books not readable, mevzuat.gov.tr unreachable) and are flagged in `groups.yaml`; the
  refit after the layout must fit re-solved pieces (asset None) and code-typed proposals.
- **T4**: the dry re-check cannot measure the build's scene, view, look and vision checks before a build; such
  findings on a changed target count as gone and are re-measured next round (marked `carried`); the scheduler
  default `agent_rounds` is still 4 (round 2); the vision critic is still asked for every room with a preview.
- **T5**: every bpy part is untested here (shell layers, rigs, sun-disc world, project WB, VRAM); the sun-disc
  calibration is an assumption until `SUN_DISC_RATIO` is measured; `RIG_GAIN` 4.0 is a documented choice; the
  imperfection overlay is procedural noise (no CC0 smudge image in the catalogue); `wenart/run/cli.py` does not
  forward `--cameras-from / --cameras-extra` (the environment drives the replay; round 2).
- **T6**: Sapling install, Poly Haven 2K downloads (fir_tree_01 alone 510 MB) and the ambientCG atlases run first on
  P1; the leaf atlases' opacity map needed the `OPTIONAL_SUFFIXES` change (applied in the integration); real04 ext_6
  stays dropped (copy b2 across a 6 m gap, a camera-search change outside D8); parking spk_001 stays a draped slope;
  hedge and tree species are inferred (no CC0 olive, cypress, plane or palm model); the new manifest kinds fall back
  to site_area / site_boundary / site_decor until `common.KINDS` lists them (round 2); `site.platforms` are recorded
  in the scene manifest only; `WENART_ASSETS` must be exported by the jobs (site_ab.sh does).
- **T7**: `catalog.SOURCES` must accept `hssd` before P2's catalogue step or every HSSD entry is dropped (round 2);
  whether `units_anchor` runs over the whole library (197 anchors, today's only relaxed-mode toilets, basins and
  stoves) is a lead / user call; the HSSD terms acceptance behind the pod's `hf_token` is checked at run time only;
  the 18 audit-removed NC / SA Objaverse entries could be reinstated for relaxed mode by a new audit decision; the
  701 untagged models are not re-asked on P2.
- **T8**: metrics 10 and 11 read "no data" until T5 and T6 write the manifest records; metric 15 needs the reviewer's
  per-view rubric JSON for the after-runs; metric 17 is a stage sum, not wall time; metrics 7 and 8 differ from the
  §7 estimates by definition (a §7 footnote is due); `wenart/assets/objaverse.py` should write the new fields for
  new entries through `catalog.licence_fields` (T7 ask).

### 14.5 The round-1 integration

The integration agent ran `pytest -m "not gpu"` over tests/ in six chunks on the quiet tree (16:21-16:43): **4,866
passed, 211 skipped, 4 xfailed, 1 failed, 139 deselected (gpu)**; `python3 -m compileall` clean, `bash -n` clean on
the four new scripts, `wenart.building.validate` accepts the three committed `building_final.json`, no key or token
in the diff. Cross-track changes it applied: `tests/gpu/test_m13_light.py` module-level skip without Blender (the
same-basename twin aborted the collection); `stages.AGENT_CODE += wenart/assets/**`; `scene_checks.usable_asset`
takes the fitted licence mode and S6 accepts a module / parametric piece whose `library_gap` names the ladder step
(D4); `cameras.REPLAY_OPTIONAL += site_view, aerial_allowed, horizon_frac`; `furniture.LICENCE_FLAGS` takes the
§13.3 flag words; `sheets/to_building.py` copies the sheets' hedges into `site.hedges` (a fresh run would lose
them otherwise); `ambientcg.OPTIONAL_SUFFIXES += opacity`. Ten test failures fixed: the bed v2 part list in
`test_look_m6` (T2 and T5 both proposed it); the camera-search bed profile (frame box + mattress box, 0.0009 off
instead of 0.0104; the real02 share 0.0694 unchanged); `rest.place_leaning` on a sideways single bed (pillows read as
arms); three `test_recolour_apply` tests (K2 ranks a real product first, `preference: True`, the D4 ladder ends in
`parametric`, not `none`); `program.room_kind` (a read `storage` room is no bedroom on a generic "Oda" label);
`test_reading_building` (a 1.9 × 1.7 m box in a living room is the missing corner sofa under K3); `test_pipeline`
(the PDF-only sofa is typed by code); two `test_real01` tests (8 of 17 untyped candidates typed by code).

**The one red test** is data, not code: `tests/test_models_assets.py::test_catalog_ids_exist_on_the_api` asks the
live Poly Haven API, which now reports `vintage_wooden_drawer_01` at 1.715 × 1.007 × 1.091 m against the committed
0.858 × 0.457 × 0.545 m (the entry is identical on HEAD); a fetch of the current files fails on an md5 mismatch of
the 8k `.bin`, so the asset is being republished. No hand-check exception was added because the file could not be
checked by hand. Lead decision: re-fetch and re-measure the asset on the next library pod (P2) once the CDN and the
API agree, or drop / replace the entry. The design-level asks the integration left for the lead are the round-2
list of `docs/progress.md` (the HSSD catalogue source, the K3 ingest order, agent rounds 3 in the scheduler and
CLI, rug members and candidate application in `edit_ops`, `common.KINDS`, the CLI replay pass-through, the manifest
records for metrics 10 and 11, `tests/test_m13_contracts.py`, the jobs `m13_p1.sh` / `full.sh` and the docs).
