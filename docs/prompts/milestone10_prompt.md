# Prompt for Milestone 10 (copy everything below the line into a new session)

Written 8 Oct 2026 from the state after Milestone 9 and the real02 run 1 (`needs review`).

---

Read `CLAUDE.md`, `docs/plan.md`, `docs/progress.md` (Milestone 9 and the real02 run) and `docs/gpu-log.md` first.
Tell me where you run (cloud or Mac). Develop on branch `opus_branch_03`. Today is <date>.

This is **Milestone 10**. It has three features. Write the spec `docs/milestone10.md` first (same layout as
`docs/milestone9.md`: goal table, one section per feature, acceptance table, pod plan, cost estimate), show me
the open questions at the end of this prompt, and wait for my answers before you write code.

## Why

| Problem today | Evidence |
|---|---|
| A room with drawn furniture keeps only the drawn pieces. A bedroom with only a bed drawn gets no nightstands, no wardrobe, no chair. | `CLAUDE.md` furniture rules; `wenart/furniture/layout.py` furnishes only rooms with no documented furniture |
| A sheet with several drawings is read as one floor plan. real02 (`one_building.dwg`) holds the basement plan twice (one is the alternative "Açık mutfak", open kitchen), the ground floor, the attic and a section side by side, so no wall was found and nothing was built. | `results/final/real02/final_report.md`, `results/final/real02/debug/one_building_dwg_p1.jpg` |
| Only interiors are built and rendered. Plot, garden and parking are "recorded, not built". There is no roof and no exterior view. | `site` block in `wenart/schema/building.schema.json` |
| The material and colour vocabulary is small: about 13 floor/wall materials, 3 wall colour words, one window frame material, one door look, no cabinet types besides the parametric kitchen counter. 7 of 12 terms of the real02 brief are unmatched: `warm greige walls`, `light grey fabric sofa`, `natural light wood furniture`, `glass coffee table`, `palms`, `monstera`, `dark bronze window frames`. | `wenart/style/vocabulary.py`; `python -m wenart.style projects/real02` |

## Feature 1 – AI generates furniture in rooms that already have drawn furniture

Goal: in a room with furniture in the documents, AI may **redesign the drawn pieces** and **add** the pieces
that are missing for the room type (for example nightstands next to a drawn bed, chairs around a drawn dining
table, a wardrobe in a bedroom with only a bed drawn, a TV unit opposite a drawn sofa). For drawn pieces only the
**location and position** are locked; everything else may change.

Rules:
1. Drawn pieces: what is locked and what may change.

| Locked (never changes) | May change by AI |
|---|---|
| location: the piece's centre point on the plan (level, room, x/y of the drawn footprint centre, ± 5 cm) | type (within the types the room type allows, for example a drawn double bed may become a different bed type, a drawn 3-seat sofa a corner sofa) |
| position: the orientation (front direction, `front_deg`, ± 1°) and the wall it stands against, if any | footprint size (width, depth), height, model, design, materials, colours |

   - Today `wenart/furniture/fit.py` `FROZEN_KEYS` freezes `type`, `footprint`, `front_deg`, `height`, ... with a
     byte comparison. In `complete` mode, replace that with a check of the locked items above (centre ± 5 cm,
     front ± 1°, same against-wall side); the check fails the stage if a drawn piece moved or turned.
   - A changed drawn piece keeps `from_documents` (its location and position come from the documents), gets
     `modified_by_ai: true` and records the drawn values (`drawn_type`, `drawn_footprint`, `drawn_height`) and the
     model answers as evidence. The report lists every change, per room: drawn type/size → new type/size.
   - A new footprint grows or shrinks around the locked centre (against-wall pieces: from the wall line) and must
     pass every placer check below; if it cannot, the next smaller option is tried, and at the end the drawn
     size is kept. Never a change that blocks a door, a window or a walkway.
   - Drawn pieces whose type was `unverified` keep that status for the drawn values; the AI type is a proposal
     and is shown in the debug image.
   - Fixed equipment stays as drawn (stairs, kitchen counter runs, sanitary ware: toilet, washbasin, shower,
     bathtub), because it hangs on plumbing and structure; ask me if any of these may change too.
   - Brief key `furnished_rooms_keep_size: true` keeps the drawn type and size and lets AI change only the look
     (today's behaviour for drawn pieces).
2. New brief key `furnished_rooms: keep | complete` in `wenart/defaults.yaml` (`keep` = today's behaviour).
   Ask me which one is the default. Rooms the brief lists under `furnished_rooms_keep: [room ids or labels]`
   always stay `keep`. Rooms that are never furnished stay so (for example Pooja, store rooms by rule).
3. Same method as empty rooms (Milestone 4): Qwen3-VL-8B, two passes, temperature 0, strict JSON schema. The
   question gives the room polygon, doors, windows, the drawn pieces (type, box, front, locked centre and
   front) and the list of types the room type allows. The answer has two parts: changes to drawn pieces (new
   type, size, style) and added pieces. Only types the room type allows may be proposed; added pieces only for
   types not already covered.
   No second anchor (no second bed in a single bedroom, no second sofa, no second toilet) unless the room type
   rule says so. Pairs are allowed (2 nightstands, 4–8 dining chairs by table size).
4. Every proposal goes through `wenart/furniture/placer.py`: inside the room, no overlap with drawn or added
   pieces, door approach and swing arcs free, 0.9 m walkway between doors and windows, window band rule,
   against-wall rule. Changed drawn pieces are placed first (at their locked centre and front), then added
   pieces. An added piece that cannot be placed is dropped, never forced; a changed drawn piece that cannot be
   placed falls back to its drawn type and size. Keep only changes and pieces both passes agree on (or a placed
   piece of one pass with confidence 0.6, as in M4).
5. Labels: added pieces are `added_by_ai` with `completes_room: true` and the model answers as evidence;
   changed drawn pieces are `from_documents` with `modified_by_ai: true` (rule 1). The debug image and the
   report show three colours per room: drawn as drawn, drawn but changed by AI (with the drawn outline dashed
   under the new one), added by AI.
6. AI decor (Milestone 9) runs after the completion, so the new pieces get decor too.
7. The vision check, the plan cross-check and the added-object detector must use the final building JSON
   (changed and added pieces), so a changed type or size and an added piece are not flagged as mismatches or
   insertions; the cross-check against the source plan checks the locked centre and front of every drawn piece.
8. This changes two `CLAUDE.md` furniture rules ("same type, position, orientation and footprint size as
   drawn" and "Rooms that have furniture in the documents: never add, remove or move furniture"). Propose the
   new wording (drawn pieces: location and position locked, never removed; type, size and look may change with
   `furnished_rooms: complete`, labelled `modified_by_ai`; additions labelled `added_by_ai`) and edit
   `CLAUDE.md` only after I say OK.

## Feature 2 – sheet analysis first, then the whole building, then exterior renders

### 2.1 New first stage: `sheets` (before `pipeline`)

Goal: understand what is drawn on every sheet before any wall is read.

1. **Split** every DWG/DXF model space and layout, and every PDF page, into drawing regions. Vector first:
   cluster entity boxes with gaps, use frames, viewports and title blocks; ignore stray far-away entities
   (real02 has one) and list them. Raster pages: the existing crop-to-drawing code, extended to several regions.
2. **Classify** each region: `floor_plan`, `alternative_floor_plan`, `section`, `elevation`, `roof_plan`,
   `site_plan`, `detail`, `3d_view`, `title_block`, `legend`, `other`. Evidence order: the region's own title
   text (TEXT/MTEXT or OCR, for example `BODRUM KAT PLANI`, `ZEMİN KAT PLANI`, `ÇATI KAT PLANI`, `KESİT`,
   `GÖRÜNÜŞ`, `VAZİYET PLANI`, `1. KAT`, `ALTERNATİF`, `(Açık mutfak)`, and English, German, French titles), then
   geometry (a section has horizontal slab bands and a roof line; a plan has closed wall loops), then two AI
   passes on a rendered crop (temperature 0, strict schema). AI proposes, title text and geometry decide.
3. **Levels**: map each plan to a level (basement −1, ground 0, upper floors, attic/roof) with its evidence.
4. **Alternatives**: two plans of the same level form one group: one `base` and one or more `alternative`s,
   each with its title (for example "open kitchen"). Which one is the base: the one without an alternative word
   in its title; if unclear, mark `unverified` and ask through the report. Never merge two alternatives.
5. **Registration**: put all plans of one building into one frame. Use the outer outline, the stair core,
   structural grid lines and columns; check the outline across floors (existing cross-check) and that the
   stairs line up. Shift and rotation are recorded with their residual; a residual over 5 cm is a conflict.
6. **Heights** from the section and elevations: floor-to-floor heights, slab thickness, ceiling heights, roof
   pitch, ridge and eaves heights, attic knee wall height, ground level. Each value has evidence (region,
   entity ids, method). What no drawing gives is `assumed` and listed, never invented.
7. **Exterior evidence** from elevations, roof plan and site plan: facade materials where hatched or labelled,
   window and door positions seen from outside (cross-check against the plans), balconies, terraces, roof type
   (flat, gable, hip, mansard, as drawn), chimneys, plot wall, paving, garden, parking, trees.
8. Output: `results/run/<p>/sheets.json` (every region with box, class, level, variant, title, evidence,
   confidence) and one debug image per sheet with every region boxed and labelled, coloured by method and
   confidence. The `pipeline` stage then reads each plan region as its own page.
9. Stop rules (`CLAUDE.md`): missing scale or no closed outer walls on a needed plan → `needs review` with the
   region named. Ask me whether a failed upper level may be left out (built and listed as missing) or stops the
   whole project.

### 2.2 Build the whole building

1. Building JSON: `levels` get `variant_group` and `variant` (`base` / alternative name); new top-level
   `variants` (one entry per buildable combination, for example `base` and `basement: open kitchen`); new
   `roof`, `facade` and `slabs` blocks; `site` elements become buildable. Update the schema, the example and
   the validators.
2. Blender: stack all levels at their elevations with slabs, stairs that connect the levels through a slab
   opening (the stair void), the attic with sloped ceilings from the section, the roof from the section and roof
   plan, the facade material on the outer wall faces, window frames and glass visible from outside, sills,
   balconies with railings, the plot and site (ground plane, paving, grass, plot wall, parking) when the brief
   allows it. Every added detail that no drawing gives is labelled `assumed` in the scene manifest.
3. One scene per variant: the base building, and one per alternative (only the alternative level changes).
   Interior renders run per variant only for the rooms that differ, so nothing is rendered twice.
4. The 3D files of Milestone 9 (`<project>.blend`, `<project>.glb`) now hold the whole building, one file pair
   per variant.

### 2.3 Exterior renders

1. Cameras: 4 eye-level views (1.6 m) from the plot corners or 10–15 m away, aimed at the two facades of each
   corner, one 3/4 aerial view, and one view per drawn elevation (same direction as the drawing). Never inside
   a wall, a tree or the plot wall; straight verticals with lens shift.
2. Light: the HDRI and sun of the style, with the building's north from the site plan if drawn (else `assumed`
   and listed).
3. Exterior style from the brief (new key `exterior:` with facade, roof, window frame, door, paving, garden
   words) and the style photos; documents win where they say something.
4. Checks: the existing gate and vision check run on exterior views too; plus a check of each elevation view
   against its drawn elevation (window and door count and positions per facade, ridge and eaves height).
5. AI polish of exterior views under the same gate (calibrated per project).
6. Report: a "Building" section with levels, variants, heights (drawn or assumed), roof, facade and a contact
   sheet of the exterior views per variant.

### 2.4 Test data

- New synthetic project `synthetic-07`: one DWG/DXF sheet in model space with a basement plan, its alternative,
  a ground floor, an attic plan, a section, two elevations and a site plan, plus a stray entity, with ground
  truth (`docs/synthetic.md`). CPU tests for split, classify, levels, variants, registration and heights.
- `real02` is the real acceptance project.
- No regressions: synthetic-03 (3 levels on separate pages) and the other projects must keep their results.

## Feature 3 – a larger material, colour and furniture library

All new entries keep today's rules: textures CC0 only (Poly Haven, ambientCG) with ids verified against the
live APIs (if the session cannot reach a site, verify on the pod and record it); furniture models from ABO,
Objaverse (licence flagged) and TRELLIS.2 for gaps, each judged by both vision models on thumbnails, front
agreed, style tags; credits in `ATTRIBUTION.md`. Keyword tables stay deterministic; unknown words are listed,
never guessed.

| Area | Today | Target |
|---|---|---|
| Colour vocabulary | white, cream, charcoal | ≥ 40 named colours (whites, greige, taupe, beige, sand, grey shades, anthracite, black, sage, olive, forest green, navy, dusty blue, terracotta, rust, mustard, blush, burgundy, …) as documented sRGB values (cite the source of each value), converted to linear RGB; light/dark/warm/cool modifiers; colour words work for walls, fabrics, cabinets, doors, window frames |
| Wall finishes | plaster white/cream/charcoal, brick, wood panel | paint in any colour of the vocabulary, lime plaster, microcement, Venetian plaster, wallpaper (≥ 6 patterns), wood slat panelling, stone, brick variants, exposed concrete; one accent wall per room by brief ("one sage accent wall"); two-colour briefs ("charcoal and white") no longer drop a colour |
| Wet walls | one procedural tile | subway, large-format porcelain, zellige, hexagon, mosaic, marble slab; tile size, colour and grout colour from the brief |
| Floors | oak light, walnut, parquet, concrete, terracotta, marble, light tiles, carpet | ≥ 25: oak natural / white-washed / smoked / grey, wide plank, herringbone and chevron in 3 tones, walnut, ash, bamboo, terrazzo, travertine, limestone, slate, large porcelain, cement tiles, hexagon tiles, vinyl, cork, carpet in vocabulary colours, sisal |
| Cabinets (new types) | parametric kitchen counter only | kitchen base and wall cabinets, tall/pantry cabinet, kitchen island, bathroom vanity, sideboard, shoe cabinet, display cabinet, built-in wardrobe; front styles flat / shaker / slatted / glass; colour and handle from the brief; worktops in stone, wood, terrazzo, steel |
| Furniture types | 24 types, ≤ 20 models each | add bar stool, bench, ottoman, office chair, console table, crib, bunk bed, chaise; ≥ 20 models per type and ≥ 3 style families per type; fabric and wood recolour of library models where the model has separable materials (else pick another model) |
| Decor | 8 types | add curtains and blinds (by window size, never covering a door), throws, books, candles, baskets, trays, clocks, sculptures, large floor plants (palm, monstera, fiddle-leaf fig, olive), pendant and ceiling lights; ≥ 15 models per type |
| Doors | one veneer look with handles | flush, shaker panel, glazed, pocket and sliding, barn, double, entrance door; oak, walnut, white lacquer, black, grey, any vocabulary colour; handles brushed steel, black, brass; the drawn opening type (swing, sliding, double) always wins |
| Windows | white painted metal frame | white PVC, anthracite aluminium, black steel, dark bronze, oak, any vocabulary colour; mullions and transoms when drawn (elevations), sills; curtains from decor |
| Exterior (for Feature 2) | grey exterior plaster | render in vocabulary colours, brick, stone cladding, wood cladding, fibre-cement boards; roof clay tiles, concrete tiles, slate, standing-seam metal, green roof; paving, gravel, grass, decking |
| Lighting moods | 5 | add bright noon, blue hour, cloudy soft, interior evening with lamps on |

Acceptance for Feature 3: `python -m wenart.style projects/real02` has no unmatched term, or each remaining term
is listed with a reason; a coverage table (types, models, style families, colours) in `docs/milestone10.md`.

## Order of work (proposal, change it in the spec if you see a better one)

1. Spec `docs/milestone10.md`, my answers, `CLAUDE.md` change for Feature 1 after my OK. Freeze the contracts
   first: building JSON schema changes (`levels.variant*`, `variants`, `roof`, `facade`, `slabs`, buildable
   `site`, `completes_room`), `sheets.json` format, new brief keys, new vocabulary slugs.
2. Then in parallel (see "Parallel work with subagents"):
   - Track A: Feature 2.1 sheet analysis + `synthetic-07` (CPU), because it unblocks real02.
   - Track B: Feature 1 (CPU + placer tests).
   - Track C: Feature 3 vocabulary, colours and textures (CPU).
   - Track D: Feature 3 library survey configs (ABO, Objaverse, TRELLIS.2 prompts) for the new types.
   - Track E: Feature 2.2 + 2.3 building, roof, facade, exterior cameras (CPU tests on synthetic-07 data from
     the frozen contract, real data after Track A merges).
3. One library pod for new models and judging, which also runs the AI passes of the sheet analysis.
4. Code review of the milestone (several lenses, adversarial verifiers, a failing-then-passing test per
   confirmed finding), as in earlier milestones, with parallel finders.
5. Full runs: real02 (all variants), real01, synthetic-03, synthetic-07; GPU tests green.
6. Commit and push after every merged track; update `docs/progress.md` and `docs/gpu-log.md`.

## Parallel work with subagents (option, default: on)

Goal: build faster by running independent tracks at the same time, and spend fewer tokens by giving routine
work to cheaper models. I can turn this off with "parallel: off"; then you work through the tracks one by one.

1. **You are the lead.** You write the spec and the contracts, split the work, launch the subagents, review and
   merge their work, run the full test suite, own git (commit, push) and own every pod. Subagents never push,
   never start, stop or create pods, never call `scripts/gpu_run.py` with a cost, and never read or print secrets.
2. **Show me the plan first**: a table of tracks with the subagent, its model, the files it owns, the tests it
   must pass and the expected size. Launch after my OK.
3. **Isolation**: each code-writing subagent works in its own git worktree (Agent tool `isolation: "worktree"`)
   on a branch `m10-<track>` made from `opus_branch_03`. You merge each finished track into `opus_branch_03`,
   run `pytest -m "not gpu"` after every merge, then push. One owner per shared file (`building.schema.json`,
   `defaults.yaml`, `vocabulary.py`, `wenart/run/scheduler.py`, `CLAUDE.md`): only the lead edits them; a
   subagent that needs a change asks the lead in its report.
4. **Model per task** (cheapest model that does the job well; move a task up a level if its result fails review):

| Model | Use for |
|---|---|
| Opus (lead and hard tracks) | spec, contracts, merges, sheet split and registration (Track A), Blender building, roof and stairs (Track E), placer changes (Track B), adversarial verifiers in the code review, anything touching the no-hallucination rules |
| Sonnet | vocabulary and colour tables with cited sources, texture id checks against the live APIs, library survey configs, synthetic-07 generator and ground truth, CPU tests, report and docs sections, review finders |
| Haiku | read-only searches (or the `Explore` agent), listing files, reading logs and pod output, counting coverage, checking that ids and paths exist |

5. **At most 4 subagents at a time.** Each prompt you give a subagent contains: the `CLAUDE.md` rules that
   apply, the frozen contract, the files it owns, what it must not touch, the tests to pass, and the report
   format: files changed, tests run with pass/fail counts, open issues, anything `unverified` or `assumed`.
   Background agents by default; do not wait idle while they run.
6. **Trust but check**: a subagent's report is a claim. Before a merge, read its diff, run its tests yourself,
   and check that nothing changed outside its files. Rejected work goes back to the same subagent with the reason.
7. **Workflows**: you may use the Workflow tool for the code review (finders in parallel, verifiers per finding)
   and for repeated batch checks (for example texture id checks), under 10 agents per workflow.
8. **GPU stays serial**: one pod at a time (`CLAUDE.md`). Parallel speed on the GPU comes from batching inside
   the pod (several projects and AI passes per pod), not from more pods. If you think two pods at once would save
   real time, show me the saving and the cost; that needs a `CLAUDE.md` change and my OK.
9. Report per track in `docs/milestone10.md` §"As built": who built it (model), time, result.

## Limits (from `CLAUDE.md`)

- GPU: the runner's priority list, ≤ $5/h, ≤ $30/day, ≤ 2 h per pod, one pod at a time, every pod stops itself.
  Batch work: the library pod also runs the recognition/sheet AI passes; the full-run pod runs all projects.
- Give a cost estimate per pod in the spec. Ask me before any single action over $5 or any limit change.
- No pod may be running when the session ends.

## Acceptance

| # | Check | Target |
|---|---|---|
| 1 | real02 end state | `ok` (was `needs review`) |
| 2 | real02 sheet analysis | 4 plans found (basement, basement "open kitchen", ground, attic) + 1 section; stray entity listed; levels and variant group right |
| 3 | real02 build | 3 levels stacked, stairs connect, attic roof from the section, heights with evidence or `assumed` |
| 4 | real02 renders | interiors per variant (only changed rooms twice) + ≥ 5 exterior views per variant |
| 5 | synthetic-07 | every region class, level, variant and height equals the ground truth |
| 6 | Feature 1 | in `complete` mode, ≥ 1 added piece in each furnished bedroom and living room of real01/real02 where the room type misses one; every drawn piece keeps its centre (± 5 cm) and front (± 1°), checked against the source plan; every type or size change listed with the drawn values; 0 placer violations |
| 7 | Feature 3 | real02 brief fully matched (or reasons listed); coverage table meets the targets above or says why not |
| 8 | No regressions | synthetic-03 and real01 results as in M9 or better; `pytest -m "not gpu"` and `pytest -m gpu` green |

## Questions to ask me before you start

1. Feature 1 default: `furnished_rooms: complete` for every project, or `keep` unless the brief says `complete`?
2. Variants: render every alternative, or only the base plus alternatives the brief names?
3. A level that fails (no scale, open walls): leave it out and list it, or stop the whole project?
4. Site: build plot, garden and parking for exterior views, or only a neutral ground plane?
5. real02 exterior style: tell me the facade, roof and window frame look, or should defaults from the interior
   style apply (listed as assumed)?
