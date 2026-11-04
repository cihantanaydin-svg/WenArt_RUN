# Milestone 14 (proposed and approved 4 Nov 2026, user: "yes"): structure recognition that learns

Goal (user, 4 Nov 2026): "I want structure recognition to be cumulatively better with the feedbacks I am giving, and
some AI or something else to give the feedbacks by itself instead of me at some point."

## 1. Why the current loop cannot become cumulative

| today | consequence |
|---|---|
| a correction of the user becomes one hand-written rule (about 40,000 lines in `wenart/ingest`, `wenart/sheets`) | the rule fixes the case it was written for; whether it helps or hurts the other 20 projects is not measured |
| the reader makes one decision per place by fall-through rules (wall or notation, gap = door / window / open / wall, inside or outside, stair or tile grid, region class) | an undecided place gets the first rule that fires; there is no margin, so nobody knows where the reading is unsure |
| a level whose outer walls do not close is left out whole | 11 of 21 real projects lose levels over cracks, glazed runs and frames the reader does not bridge; the 95 % that was right is never seen |
| one reader (vector geometry); AI only classifies undecided regions and types symbols | no second opinion exists, so only the user can see that something is wrong |
| the regression set compares counts with the last accepted reading | it stops regressions; it cannot say how far a reading is from the truth, nor which rule helped |
| the user reviews free text on comparison sheets | the user's time is the only reviewer and nothing runs when the user is not looking |

## 2. The new mechanism in one paragraph

Every decision the reader makes becomes a **candidate with a score and a margin**. The scores come from a **ranker
trained on the user's corrections** (today's hand rules are its features, not its verdicts). A low margin goes to
**independent second opinions** (a raster reading of the same plan, the vision model) and to **cross-document checks**
(sections, elevations, site plan, mirrored halves, typical floors, size tags, area tables). What stays unsure goes to the
user as an **accept-or-reject item**, never as a free-text review. Every accept or reject is a **labelled example** in
the correction store, the ranker is retrained, the regression set is re-scored. The reviewers' **trust** (their
precision against the user's answers) is measured; a reviewer above the threshold auto-accepts its own findings. That is
how the user's feedback compounds and how the user is replaced step by step.

## 3. Tracks

### R1 Correction store and truth (the memory)
- `results/reading_truth/<project>.json`: per level the elements the user confirmed (levels and elevations, rooms with
  label and area, doors, windows, stairs with arms and risers, the outline, the core, twins, typical floors, open
  recesses, balconies), each with `source: accepted_reading | user_correction | synthetic`.
- `results/reading_corrections.jsonl`: one record per correction: project, level, place (building metres and the
  drawing's box), element id, the reader's answer, the right answer, the user's words, the lesson id, the date. The
  3 and 4 Nov corrections (UL274 to UL328) are backfilled from the progress file first.
- A reading **score** per project: recall and precision per element type against the truth, weighted
  (levels 5, rooms 3, stairs 3, doors 2, windows 2, walls 1), one number; `results/reading_scores.json` per commit.
  Gate: a change is accepted when the total rises and no project falls by more than the tolerance.

### R2 The candidate reader (never silent, never leaves a level out)
- The decisions above return `[(candidate, score)]` with the winning margin; every element carries `confidence` =
  the margin, `decided_by: rule | ranker | raster | vision | user`.
- Closure: the best closure the reader finds (short joins, crack joints, glazed runs, the mirror twin, the typical
  floor above or below, the drawn outline) is built with its confidence; a level is left out only when no closure
  exists at all. The reading check gets RC7 "low-confidence places" (listed first, drawn in their own colour on the
  comparison sheets).
- Expected first effect: real09, real11, real13, real14, real16, real18 go from "levels left out" to "levels read,
  places to check".

### R3 The ranker (the generalisation engine; design of 4 Nov 2026, evening)
- A small open-source model per decision kind, trained on CPU in seconds: one-vs-rest logistic regression written in
  numpy, its standardisation and coefficients stored as JSON in `wenart/reading_check/models/<decision>.json` with the
  commit, the projects and the metrics it was trained on (no pickles, no new dependency, reproducible). Gradient
  boosting only if the linear model is shown to lose on held-out projects.
- Four steps, in this order: (1) **instrument**: every reading writes `report["decisions"]`, one record per decision
  (kind `gap_kind` | `wall_or_notation` | `inside_or_outside` | `stair_or_grid` | `region_class`, the element, its
  place in building metres, a flat dict of numeric features, the rule cascade's answer with a rule confidence from a
  fixed table (a swing arc 0.95, a named door 0.9, an open leaf 0.8, a window of 3 or more lines with glass 0.9, of 2
  lines 0.6, doorless 0.5, unclassified 0.2 ...), the final answer after every later pass, `decided_by`); (2)
  **label**: a pure join of the decision records with the truth (the nearest truth opening within 0.5 m and 0.3 m of
  width gives a gap its class; a truth wall covering a stroke makes it a wall; a gap on the outline with nothing in the
  truth is open air); (3) **learn**: leave-one-project-out, the weights of the labels are not equal: a user correction
  counts 10, a synthetic truth 3, an accepted reading 1, because the accepted readings are the reader's own answers
  (training on them alone teaches the ranker to copy the rules; the corrections are where the rules were wrong and the
  synthetic cases are exact); the report compares the ranker with the rules on every project and, above all, on the
  corrections (how many of the user's corrected cases it now gets right without breaking the accepted ones); (4)
  **integrate**: the ranker scores the candidates after the rule cascade; it decides only where the rule confidence
  is under its threshold and its own margin is over its threshold (`decided_by: ranker`, logged with both); a hard
  constraint that is physics stays a rule (a gap with a swing arc is a door, a door is never wider than its wall run);
  a low margin on both sides is an RC7 place and, in the pod, a question for the vision model (UL329).
- The ranker never draws geometry: it ranks code-built candidates.
- Report per retrain: which features carry which decision; a feature that no longer matters is a rule that can go.

### R4 Independent second opinions (the first automatic reviewer)
- The raster reader (`wenart/ingest/raster.py`) already reads scans into the same `GenericPage`. Render every vector
  plan region to an image and read it with the raster path too: two readers, one drawing. Where they disagree
  (a wall one has and the other lacks, a room one closes and the other opens, a stair one sees) is a finding with both
  readings as evidence. No user needed.
- The vision model (Qwen3-VL / GLM-4.6V on the pod, the two-pass agreement of `recognition.detect`) extracts a coarse
  plan from the region image: rooms with labels, door and window counts per room, stairs, outside spaces. Compared
  with the vector reading per room: a third opinion, cheap (one short pod, about 10 min per batch of projects).
- These do not change the model (trust order stays vector > OCR > AI): they produce findings and ranker features.
- Known risk of the raster second opinion: on a vector plan drawn as face lines (no fill) the raster wall mask may
  miss what the vector reader sees, and the disagreement becomes noise. So the raster opinion is calibrated on the
  accepted projects first (its precision against the accepted readings), its trust goes into the R9 ledger, and it
  gates nothing until it earns it. The vision model is the stronger second opinion and needs the pod.

### R5 Cross-document consistency (the second automatic reviewer)
- Plans against sections: storey count and heights, the ground, the roof; against elevations: windows per facade and
  floor (the reader already extracts the elevation openings and never compares them); against the site plan: number of
  buildings, footprint, orientation; against size tags and schedules: doors and windows read versus tagged; against area
  tables ("Net Alan", flat types): rooms per flat; the mirrored half against its twin; the typical floor against its
  copies; the core against every level.
- Each disagreement is a finding with the two sources named; many of the user's corrections of 3 and 4 Nov (storey
  heights, the missing window on L1 to L6, the second villa, the pool, the garage door) would have been raised by these.

### R6 The critic with the user's question bank (the third automatic reviewer)
- The reading lessons' questions (39 today) and the architectural sense checks (every level reachable by a stair,
  every room with a door, every flat reachable from the entrance, no label outside a room, no room behind a facade gap
  as wide as itself, no stair that is a tile grid) are asked of every reading: by code where measurable, by the vision
  model on the comparison sheets where not.
- Calibration before trust: run the critic on the readings as they were before each of the user's corrections and
  measure recall (how many of the user's findings it raises) and precision (how many of its findings the user accepts).
  Both are reported with every run. The critic gates a reading only above the agreed thresholds.

### R7 Synthetic failure classes (truth without waiting for a new DWG)
- `wenart/synthetic` already writes deterministic DXF projects with known truth. It gets one generator option per
  failure class the user found: letter-spaced labels, two-stub jambs, glazed corner facades, dimension chains beside
  walls, mirrored halves, typical floors, plans titled only by elevation, winder and curved stairs, sheet frames with
  several titles, sections naming storeys, open recesses, parapets, garages with wide doors, lift shafts.
- Rule: a reading lesson is `built` only with a synthetic case or a project fixture and a truth entry; a CPU test over
  the lessons file enforces it. The synthetic set also feeds R3's labels in several drafting styles.

### R8 Stability tests (fragility without a user)
- Every project read again mirrored, rotated 90 degrees, scaled to millimetres, with generic layer names and with the
  text layers removed (ezdxf transforms of the converted DXF); each variant's reading is scored against the original
  reading as its truth with R1's matcher, so the stability score is the reading score itself; a place that changes is a
  fragile decision: it is a finding, a ranker example and a sign of a rule that trusts one drafter's habit (UL262's
  layer words are a feature for the ranker, never the only evidence).

### R9 The user's detailed reviews stay; the machine's findings get accept-or-reject (user, 4 Nov 2026: "accept and
reject might be not enough, possibly I may need to continue detailed reviews for some time more")
- The user keeps reviewing the sheets in detail, in free words, as long as the user wants. What changes is the capture:
  every remark is turned at once into a correction record (R1) with the level, the place and the element the AI
  locates from the remark and the sheet, and the crop is shown back in the reply so a misplaced record is caught in the
  same exchange. One remark gives one truth entry, one correction record and, when general, one lesson with a
  synthetic case. The detailed review trains the ranker directly.
- The sheets are made for detailed review: low-confidence places in their own colour and numbered ("place 7"), the
  reviewers' own findings pre-marked, the two candidates drawn where the reader was unsure.
- The machine's findings (R4 to R6, R8) go to a page like the furniture ranking page: one finding with its crop and
  its candidates, accept, reject, or a free-text answer. This is an addition for the reviewers' output, not a
  replacement of the user's review.
- A trust ledger per reviewer: precision against the user's answers over the last N findings. Above a threshold the
  user sets, a reviewer's finding is auto-accepted (written to truth, applied through the normal candidate path,
  logged); below, it waits. The ledger is in the report of every run. The user decides when to enable auto-accept.

## 4. Day plan (user, 4 Nov 2026: "the timeline is too long"); each day ends with something the user can look at

Tracks that touch different modules run in parallel in worktree agents, as the lessons of 30 Oct did.

| day | work | the user sees |
|---|---|---|
| 1 (5 Nov) | R1: correction records of UL274 to UL328 backfilled, truth from the accepted readings, the score script; R2: closure that never leaves a level out (glazed runs, cracks, the twin, the typical floor), RC7 low-confidence places; everything on all 21 real projects and the 7 synthetic ones | every real project read with every level (the 11 that lose levels today first); the first score table of all 28 projects; sheets with low-confidence colours |
| 2 (6 Nov) | R2: candidates with margins for gap kind and wall-vs-notation; R5: elevation windows against the plan, section storeys against the levels, size tags against doors and windows; R9 capture: a remark becomes a record with its crop | the sheets of every project with the reviewers' findings pre-marked, for the user's detailed review of as many as the user wants (the user's time is the only limit); every remark answered with its record and crop |
| 3 (7 Nov) | R3: ranker v1 (gap kind, wall vs notation) trained on truth and corrections, compared with the fall-through rules on held-out projects; R8: mirror, rotation, unit and layer-name stability; score per commit as a gate | the ranker's gain per project; the fragile places found by the stability tests |
| 4 (8 Nov) | R4: the raster reader on the rendered regions as a second opinion; R7: generator options for the first five failure classes; the lesson-to-test rule | disagreement findings on the open projects; the lessons file with a case per reading lesson |
| 5 (9 Nov) | R6: critic calibrated with one short pod (vision extraction and the question bank), recall and precision against the user's past corrections; R9: the findings page | the calibration table (what the machine finds of what the user found); the page with the first findings |
| 6 (10 Nov) | the trust ledger; a new DWG read end to end through the loop; corrections per project measured | the first project reviewed by the machine before the user |

After day 6 the loop runs on every new drawing; the user's detailed reviews continue as long as the user wants and
each one raises the score and the reviewers' recall. No full run is needed; pod cost of the whole milestone a few
dollars.

## 5. Measures

| measure | now | target |
|---|---|---|
| real projects read with every level | 10 of 21 | 21 of 21 (low-confidence marked) |
| reading score against truth | not measured | per commit, rising, no project falling |
| user corrections per project before "ready" | 10 to 20 | under 3 |
| reviewer recall of the user's past corrections | not measured | over 80 % on held-out projects |
| reviewer precision (accept rate) | not measured | over 70 %, per reviewer in the ledger |
| readings that change under mirror, rotation, layer renaming | not measured | 0 on accepted projects |

## 6. Rules this touches (user OK of 4 Nov 2026: "yes")

- Milestone 10 rule "AI only proposes; an agreed class never makes a region a plan": unchanged for geometry (AI never
  draws a wall), but AI and the ranker may decide between code-built candidates when the code is undecided, logged
  with `decided_by` and the margin, reviewed by R4 to R6.
- Auto-accept of a reviewer's finding above its trust threshold: the thresholds and the first enabling are the user's
  decision; until then every finding waits on the page.

## 7. First steps (day 1)

1. R1: the correction records of UL274 to UL328 and the truth of the accepted projects; the score script.
2. R2: candidates with margins for gap kind and wall-vs-notation; closure that never leaves a level out; RC7.
3. R5: windows per facade from the elevations against the plan; storeys from the sections against the levels.
4. All 21 real projects and the 7 synthetic ones from the first day (user, 4 Nov 2026: "why only 3 projects?"); real09
   (glazed facades), real10 (recess, typical floors) and real17 (core stair, shop front) are only named because they
   show three different failure classes. Every change is scored on every project.
