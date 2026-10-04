# Milestone 9 – a larger library (20 models per type, more decor) and AI decor in rooms with drawn furniture

Goal (user, 4 Oct 2026): "increase the number of furniture items, increase it to 20 per type, also increase the
decorative items; in the pipeline let AI decorate rooms where the furniture location comes from the plans", and
"include also: final results to give 3d files that can be opened in blender".

| # | Item | What it means |
|---|---|---|
| 1 | 20 models per furniture type | `catalog_library.json` keeps up to 20 accepted models per furniture type (M8: 12), for all 24 library types; types the real sources cannot fill get generated models (TRELLIS.2), as in M8 |
| 2 | More decor | up to 20 models per decor type (M8: 16), five new decor types (vase, bowl, small plant, table lamp, mirror) |
| 3 | AI decor | a vision-language model decorates every furnished room, the rooms whose furniture comes from the documents included; it chooses from checked places ("slots"), never moves, adds or removes furniture |
| 4 | 3D files | every finished project also gives `<project>.blend` (opens in Blender: packed textures, the render cameras with their metered exposure) and `<project>.glb` (glTF binary for Blender and other 3D tools), §5a |

The furniture and no-hallucination rules of `CLAUDE.md` stay: drawn furniture keeps type, position, orientation and
footprint; decor is creative AI where the documents are silent, labelled `added_by_ai`, two passes at temperature 0,
strict schema, only what both passes agree on is kept; every item passes deterministic geometry checks.

## 1. Acceptance: 20 per type, styles spread first

Session check on the committed M8 library (`results/library/accepted.json`): 247 judged models were refused only by
the per-style cap (3 per type and style family) and 44 by the per-type cap (12). Re-accepting the same judgements with
the new limits:

| Rule | Furniture models | Decor models |
|---|---|---|
| M8: 12 per type (decor 16), 3 per style family | 180 | 24 |
| 20 per type, 3 per style family | 186 | 24 |
| 20 per type, 5 per style family | 258 | 37 |
| 20 per type, 8 per style family | 306 | 48 |
| 20 per type, no style cap | 331 | 57 |

New rule (`objaverse.accept`, `objaverse.yaml accept`): `per_type_max` 20, `decor_per_type_max` 20,
`per_family_max` 5 as the **first pass** (styles spread: in rank order a model is kept while one of its families has
fewer than 5), then a **fill pass** takes the models the first pass left for their style (`over_style_limit`), in rank
order, until the type has 20 (decision note `style_fill`). Real models still rank before generated ones, so a
generated model never pushes a real one out. With the M8 judgements alone this gives the 331 / 57 of the last row;
the types still short of 20 are below.

| Type | M8 | Re-accept | Short of 20 | Where more come from |
|---|---|---|---|---|
| bathtub, shower, sink_kitchen, stove, toilet, washbasin, washing_machine, fridge | 1–4 | 1–8 | 12–19 each | Objaverse fixtures (§2.2), generated (§2.3) |
| bed_single | 8 | 9 | 11 | generated (ABO has only 12 single beds in range) |
| potted_plant | 10 | 10 | 10 | generated |
| wardrobe, nightstand, dresser | 5–10 | 16–18 | 2–4 | ABO, wider survey (§2.1) |
| the other 11 types | 8–12 | 20 | 0 | – |

## 2. New candidates

### 2.1 ABO (wider survey, three new decor types)

`abo.yaml survey.per_type_limit` 24 → **40**, `max_downloads_per_type` 36 → 60. The pick order is unchanged (round
robin over the ABO styles), so the first 24 candidates of every type are the M8 ones and keep their judgements; only
the next 16 per type are new. New decor rules (first matching rule decides; `max_height` is new: the model's height
must be at most this):

| Rule | Product types | Words / height | Type |
|---|---|---|---|
| `table_lamp` | LAMP | height ≤ 0.95 m; not floor, standing, torchiere, clamp, clip | `table_lamp` |
| `vase` | VASE | not wall mount, hanging | `vase` |
| `vase_named` | PLANTER, HOME, HOME_FURNITURE_AND_DECOR | vase; not wall mount, hanging, planter (before the `plant` rules) | `vase` |
| `mirror` | HOME_MIRROR | not floor, standing, full length, leaner, storage, jewelry, cabinet | `mirror` |
| `mirror_named` | HOME, HOME_FURNITURE_AND_DECOR | mirror; not floor, standing, full length, leaner, storage, cabinet | `mirror` |

The listings were read in the session (4 Oct 2026, `abo survey --metadata DIR --no-download`); the counts are in
§2.4.

### 2.2 Objaverse fixtures

The M8 survey refused most sanitary and kitchen objects before judging: toilet 35 of 48 tried were `untextured`, and
49 of 111 failed the face count. Plain sanitary ware and appliances look right with flat material colours (white
ceramic, enamel, steel), so for the fixture categories (`toilet`, `sink`, `bathtub`, `refrigerator`, `stove`; new
`objaverse.yaml prefilter.overrides`) a model without textures is taken when its materials have colours, the face
count range is 800–400,000 and up to 40 candidates are kept (80 tried). The other categories are unchanged (their
pick order and candidates stay the M8 ones). The judges still decide the quality (≥ 4 from both).

### 2.3 Generated models up to the target

`python -m wenart.assets.generate plan --target 20` (new mode; the M8 gap mode stays the default): for every
generated type (furniture without fixed equipment, plus the decor types `vase`, `bowl`, `plant_small`) the plan reads
the accepted list over **every** source (real and the generated models of earlier pods), counts the accepted models
per type, and plans `ceil(deficit / 0.7)` new candidates (0.7 = the share of M8's generated candidates that passed the
judges). The candidates go round robin over the nine style families (the family with the fewest accepted models of
the type first, then the vocabulary order), each one a new image index of its (type, family) pair after the indexes
done before (`img_3`, … for M8's pairs), so earlier images and models are never redone. Items are ordered round by
round (the first new candidate of every type, then the second, …; types with the larger deficit first), so a deadline
cut leaves every type with candidates. Decor prompts use the family's new `decor` hints (`generate.yaml`).

### 2.4 Expected sizes

Counted in the session on the ABO metadata of 4 Oct 2026 (mapped / in the size range); see §9 for the numbers measured
on the pods.

## 3. Decor types

| Type | Where (slot kind) | Typical size w × d × h (m) | Library | Parametric fallback |
|---|---|---|---|---|
| `cushion` | sofa back, bed head, armchair | 0.45 × 0.15 × 0.45 | ABO PILLOW | soft box (M4) |
| `book_set` | bookshelf shelf, desk, coffee table, nightstand | 0.30 × 0.22 × 0.22 | – | books (M4) |
| `plant` | floor corner | 0.40 × 0.40 × 1.00 | decor plants and the `potted_plant` furniture models | pot + crown (M4) |
| `rug` | floor under a group | rule (M8) | ABO RUG | flat box (M8) |
| `wall_art` | wall above sofa, bed, dresser, desk | rule (M8) | ABO WALL_ART | none (not built) |
| `vase` (new) | tops of tables, dressers, TV units, nightstands, side tables | 0.15 × 0.15 × 0.30 | ABO VASE, generated | lathe vase |
| `bowl` (new) | coffee and dining tables, dressers | 0.30 × 0.30 × 0.10 | generated | shallow bowl |
| `plant_small` (new) | tops of side tables, nightstands, desks, dressers, TV units, shelves | 0.20 × 0.20 × 0.35 | generated | small pot + crown |
| `table_lamp` (new) | nightstands, side tables, desks, dressers | 0.30 × 0.30 × 0.50 | ABO LAMP ≤ 0.95 m | base + stem + shade (unlit) |
| `mirror` (new) | wall above a washbasin, a dresser or a hall console | rule (as wall art) | ABO HOME_MIRROR | frame + mirror glass |

Sizes and height ranges of the new types go into `objaverse.yaml` (`types`, `decor_sizes`); the decor judge question
gets their wording (`DECOR_WORDS`): a vase is a vase (not a planter with soil), a small plant is a pot that holds a
plant, a table lamp stands on a table (not a floor, wall or ceiling light), a mirror hangs on a wall (not a floor or
cabinet mirror). Mirrors have the documented ABO front (the mirror side), the others no front. Lamps stay unlit (the
lighting of M6–M8 is unchanged).

## 4. AI decor (`wenart/furniture/decor_ai.py`)

For every room with at least one verified, built piece (documented or added by the layout), unless the brief says
`decor: false` (no decor) or `decor: rules` (the M8 rules), and never in a prayer room:

1. **Slots** (deterministic, from the building): the places decor can go, each with an id, its kind, its host or
   anchor, the decor types it allows, and the largest box an item may take there.
   - `top`: the free top of a table, side table, nightstand, coffee table, dining table (centre), dresser and TV
     unit (left and right part), desk (back left, back right); max footprint = that part of the top minus a 3 cm
     margin; max height = ceiling clearance, and when the host stands within 0.3 m of a window the sill height minus
     the host top (the placer's window rule).
   - `soft`: cushions on a sofa back (2 below 2 m width, else 3), a bed head (2 on a double, 1 on a single bed), an
     armchair (1).
   - `shelf`: books on a bookshelf (as M4).
   - `wall`: above a sofa, a bed's headboard, a dresser, a desk (wall art), above a washbasin, a dresser or a hall
     console (mirror); the M8 wall art geometry (`wall_art_for_host`: on the wall behind the piece, never over a door,
     window or opening, inside the wall segment, under the ceiling).
   - `floor`: up to two free room corners for a plant (the M4 corner check with the placer: inside the room, no
     overlap, not on a door approach or swing, the 0.9 m walkways intact, not within 0.3 m of a window).
   - `rug`: the M8 rug groups (sofa + coffee table, a double bed's foot, a dining table + 0.6 m), with the M8 rug
     geometry (`fit_rug`).
2. **Two passes** of the layout model (Qwen3-VL-8B through the vLLM server of the layout stage; text only;
   temperature 0; pass 2 with another block order and seed). The question gives the room (label, type, area), the
   style text, the pieces (id, type, size, from the documents or added by AI), the slots with their allowed types and
   sizes, and a short guide per room type (living room and bedroom 4–8 items, kitchen, bathroom, hall and dining
   room 1–4; leave some surfaces empty). Answer schema per room (strict, built for that room: `slot` and `type` are
   enums of the room's slots and the decor types, `colour` an enum of the style vocabulary's colour names):
   `{"items": [{"slot", "type", "colour", "reason"}]}`, at most one item per slot.
3. **Agreement**: an item is kept when both passes put the same type into the same slot (confidence 0.9); the colour
   is the one both passes name, else pass 1's (noted). An item whose type the slot does not allow is dropped and
   listed. Single-pass items are listed in the report as `not agreed`, never built.
4. **Checks** (deterministic, per kept item): the item box fits the slot (it is scaled down to the slot's max box,
   never up; below the type's minimum size it is refused), wall items do not overlap each other on a wall, floor
   items pass the placer checks again with every other floor item. A refused item is listed with the reason.
5. **Fallback**: a room where no item survives (both passes failed, nothing agreed, or the server was not reachable)
   gets the M8 rule decor, labelled `method: rule`, and the report says why. A dead server is never silent: the stage
   then ends `warning`.
6. **Output**: `building.decor` items as in M8 plus `method: ai`, `slot`, `colour`, `evidence` (`[{file:
   building.json, method: ai, model, pass: 1, confidence: 0.9, text: reason}, {… pass: 2}]`), `status: verified`;
   `decor_ai.json` (per room: slots, both passes, agreement, checks, fallback), `decor_report.md`, and one PNG + JSON
   per room in `decor_debug/` (room, pieces, slots, kept items coloured by kind, refused items crossed).

Pipeline: the decor stage becomes a VLM stage of the Qwen session (phase 3, right after the layout of the same
project, so no extra server start); its fingerprint covers the input building, the style, the model id and revision
and the code. A project without a Qwen session (smoke profile, `--no-ai`) runs the rule decor.

The building schema gets the new decor types, `method` `ai` | `rule`, `slot`, `colour` and `evidence`.

## 5. Builder

- Surface decor (`vase`, `bowl`, `plant_small`, `table_lamp`, `book_set` on a top) rests on the **built** top of its
  host: a ray straight down at the item centre onto the host's built mesh (library or parametric), else the host's
  built box top; an item whose centre does not hit the host mesh is moved towards the host centre (up to half the
  slot) and refused when it still does not hit.
- `mirror` hangs like wall art (`wall_art_placement`), with the parametric framed mirror when there is no library
  model; the mirror glass is a new material (`mirror`: metallic 1, roughness 0.03).
- The decor floor plant may use a `potted_plant` furniture model (same object, front-less).
- Every decor item keeps `kind: decor`, `source: added_by_ai`; its evidence method (`ai` or `rule`) goes into the scene
  manifest; surface items share their host's pass index, wall and floor items have their own (M8).
- The vision check's decor categories follow the decor types (`table_lamp` ≙ `lamp`, `plant_small` ≙ `plant`).

## 5a. 3D files (`wenart/blender/export.py`, stage `export`)

After the renders (phase 5, Blender), `python -m wenart.blender.cli export` opens `scene/scene.blend` and writes
`outputs/<p>/export/`:

- `<p>.blend`: compressed, every image packed (no path on the pod remains); textures above 1024 px scaled down,
  opaque 8-bit textures packed as JPEG (quality 90; Blender would pack a changed image as PNG, 5–10 times larger),
  textures with alpha and float images as they are; the render settings of the delivered images (Cycles, AgX,
  "AgX - Punchy", 1920 x 1080); every rendered camera carries its metered exposure (`wenart_exposure_ev`) and white
  point (`wenart_whitepoint`) as custom properties, the scene takes the first camera's; a text block
  `WENART_README` explains the file (the window pull of the delivered images is a post step, so windows render
  brighter in Blender); the objects keep their `wenart_*` properties (element id, room, type, source, asset).
- `<p>.glb`: glTF binary (modifiers applied, JPEG textures where no alpha is needed, cameras, lights).
- `export_manifest.json`: bytes and sha256 per file, the images (scaled, packed, format), the cameras and their
  exposure, the Blender version, warnings.

The stage is not critical (a failure is a warning: the renders and reports stand) and is skipped by the smoke
profile. The copy step puts the three files into `results/final/<p>/3d/`; the runner streams the `.blend` and `.glb`
past its 20 MB small-file cap (own caps: 2 GB per file, 8 GB per run) into `runs/<job>/results/final/<p>/3d/`,
after the small files. Git keeps only `export_manifest.json` (`.gitignore`: `results/**/*.blend`, `*.glb`); the
files themselves are handed to the user and stay on the Network Volume (`/workspace/outputs/<p>/export/`). Private
projects keep their 3D files in `/workspace/outputs-private/<alias>/export/` (the private allow-list is unchanged).

## 6. Pods

| Pod | Steps | Est. minutes | Est. cost |
|---|---|---|---|
| L1 | ABO survey (40 per type, new decor rules), Objaverse survey (fixtures), thumbnails, judging (2 models), accept (20 per type), catalogue | 60–70 | $2.1–2.5 |
| L2 | TRELLIS.2 setup (cached wheels), accept over every source, generation plan `--target 20`, generation (two shards) until 30 min before the deadline (`WENART_GENERATE_RESERVE_MIN`), thumbnails, judging, catalogue | 120 | $4.2 |
| L3 | the rest of the generation plan (if L2 is cut), judging, catalogue | ≤ 110 | ≤ $3.9 |
| F1 | full run of real01 only (user, 4 Oct 2026) with the new library, AI decor and the 3D files | 40–50 | $1.4–1.8 |

All on the RTX PRO 6000 ($2.09/h; worst case per pod $4.18 < $5); one pod at a time; the $30/day limit holds.

## 7. Tests

CPU: accept with the fill pass (style spread first, fill to the type limit, real before generated); ABO rules
(`max_height`, the new decor rules, prefix-stable pick order at 40); Objaverse fixture overrides; generation plan in
target mode (deficits, rounds, new indexes after the done ones, decor types); catalogue validation of the new decor
types; decor slots (every slot kind, window and ceiling limits, unverified and not-built hosts excluded, prayer
rooms); the decor schema per room (enums, xgrammar-safe keywords); agreement (same slot and type, colour rule);
checks (scaled down to the slot, wall overlap, floor placer checks); the rule fallback and its reasons; the CLI with a
fake client; the scheduler (decor in the Qwen session after the layout; rule decor without a server); builder rest
heights on a top (ray hit, moved, refused) and the mirror (Blender tests skip without Blender); vision-check
categories.
3D files: the export helpers (scaled sizes, camera exposures from the render manifest, JPEG candidates, README,
manifest with sha256), the stage and its skip in the smoke profile, the copy rule, the runner's streamed 3D files.
GPU: `test_library.py` (counts per type, the new decor types present, attribution complete), `test_m9.py` (AI decor
recorded per room with both passes and built, surface decor resting on its host, the 3D files packed and complete
with every rendered camera and its exposure).

## 8. Done criteria

CPU suite green; L1, L2 (L3) and F1 exit 0 or every failure explained; `catalog_library.json` with ≥ 20 models for
every type whose sources allow it (the report lists any type below 20 with the reason); ≥ 20 models per decor type
where the sources allow it; every furnished room of real01 decorated by AI (or the rule fallback with the
reason); the 3D files of real01 written, packed and handed to the user; renders and reports committed; `docs/progress.md`, `docs/plan.md` (sources, licences), `docs/gpu-log.md`
updated; no pod running.

## 9. As built

(filled in while running)
