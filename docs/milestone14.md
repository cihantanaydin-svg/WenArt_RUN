# Milestone 14 (proposed 4 Nov 2026, waiting for the user's OK): structure recognition that learns

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

### R3 The ranker (the generalisation engine)
- A small open-source model (gradient boosting or logistic regression, scikit-learn, CPU, seconds to train) per
  decision kind. Features: what the hand rules compute today (layer name class, linetype, length, thickness, parallel
  partner distance, text nearby, block name, swing arc, position on the outline, the mirror twin's answer, the typical
  floor's answer, the raster reader's answer).
- Labels: R1's truth and corrections plus the synthetic projects (R7). Today's accepted readings already give about
  500 rooms, 500 doors, 340 windows, 300 other openings and 3,200 walls, each a labelled decision; the gaps and strokes
  around them give the negatives.
- The ranker never draws geometry (CLAUDE.md evidence rules): it ranks code-built candidates. A rule stays as a hard
  constraint only where it is physics (a door is not wider than its wall run), everything else becomes a feature.
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
  text layers removed; the readings must agree (allowing what the removed layer carried). A place that changes is a
  fragile decision: it is a finding and a ranker example.

### R9 The review page and the trust ledger (the user's new role)
- One page per project like the furniture ranking page: one finding at a time with its sheet crop and the two
  candidates; accept, reject, or "other" with a click on the drawing. Each answer writes a correction record (R1).
- A trust ledger per reviewer (R4 raster, R4 vision, R5 each check, R6 critic, R3 ranker margin band): precision
  against the user's answers over the last N findings. Above the threshold a reviewer's finding is auto-accepted
  (written to truth, applied through the normal candidate path, logged); below, it waits for the user. Thresholds are
  the user's to set; the ledger is in the report of every run.

## 4. Phases, exit criteria, cost

| phase | work | exit criterion | where |
|---|---|---|---|
| P1 | R1 truth and corrections backfilled; the score; R2 candidate decisions for gaps, walls vs notation, closure | every real project reads every level; score reported per commit; real09, real10, real17 in the truth | CPU (here or the Mac) |
| P2 | R3 ranker for gap kind and wall vs notation; R5 sections, elevations, size tags; R8 stability | the ranker beats the fall-through rules on held-out projects; stability findings 0 on the accepted projects | CPU |
| P3 | R4 raster second opinion; R7 generator options for the known failure classes; the lesson-to-test rule | disagreement findings on the 11 open projects reviewed; every reading lesson has a case | CPU |
| P4 | R4 vision extraction; R6 critic calibrated; R9 page and ledger | critic recall over 80 % and precision over 70 % on held-out corrections; the user answers only page items | one short pod per batch (about 10 min, under $1) |
| P5 | auto-accept above thresholds; the user's corrections per project measured | under 3 user corrections per new project; new DWGs read to "ready" without the user in most cases | CPU + short pods |

No full run is needed for any phase. Pod cost of the whole milestone: a few dollars.

## 5. Measures

| measure | now | target |
|---|---|---|
| real projects read with every level | 10 of 21 | 21 of 21 (low-confidence marked) |
| reading score against truth | not measured | per commit, rising, no project falling |
| user corrections per project before "ready" | 10 to 20 | under 3 |
| reviewer recall of the user's past corrections | not measured | over 80 % on held-out projects |
| reviewer precision (accept rate) | not measured | over 70 %, per reviewer in the ledger |
| readings that change under mirror, rotation, layer renaming | not measured | 0 on accepted projects |

## 6. Rules this touches (need the user's OK)

- Milestone 10 rule "AI only proposes; an agreed class never makes a region a plan": unchanged for geometry (AI never
  draws a wall), but AI and the ranker may decide between code-built candidates when the code is undecided, logged
  with `decided_by` and the margin, reviewed by R4 to R6.
- Auto-accept of a reviewer's finding above its trust threshold: the thresholds and the first enabling are the user's
  decision; until then every finding waits on the page.

## 7. First steps (this week)

1. R1: the correction records of UL274 to UL328 and the truth of the accepted projects; the score script.
2. R2: candidates with margins for gap kind and wall-vs-notation; closure that never leaves a level out; RC7.
3. R5: windows per facade from the elevations against the plan; storeys from the sections against the levels.
4. Test cases: real09 (glazed facades), real10 (recess, typical floors), real17 (core stair, shop front).
