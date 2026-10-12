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
| D2 | HSSD: yes | HSSD (CC BY-NC 4.0, gated) is downloaded and audited in pod P2; **the user must accept the terms at `https://huggingface.co/datasets/hssd/hssd-models` with the Hugging Face account whose token is the pod's `hf_token` secret before P2** |
| D3 | keep flagged | the 281 nvdiffrast-era generated models stay usable with `licence_flag: tool_nc`; in `commercial` mode they are excluded |
| D4 | yes, "but we need a good model" | the fallback ladder is built, and the fallback must look like a real product: module builders from real module sizes with PBR slots, parametric families v2 with PBR, bevel and real proportions; every piece built below the library level is listed in the report so the gap can be closed with a real model later |
| D5 | yes | drawn groups as units (0.5 m per-member bound), product-size snap for furniture; off with `keep` / `furnished_rooms_keep_size` |
| D6 | raise to $300 | project total $300 (CLAUDE.md); the pods of §8 are approved; the M12 baselines B0 of real02/real03 run (recommended, not objected) |
| D7 | yes with my edits | `CLAUDE.md` updated (this commit) |
| D8 | no | cameras keep the M11 policy (18/16 mm at 1.25 m, hall views as today); the before/after uses the same camera records on both sides; the exterior camera bugs (site view below the horizon, dropped views behind the hedge) are still fixed because they are bugs, not policy |
| D9 | hold the paid ones | no Maxtree, no BlenderKit, no 3D-FUTURE in Milestone 13 |
| D10 | yes | AI polish stays off |

Build (step 2) follows in §13 (contracts) and §14 (build log).
