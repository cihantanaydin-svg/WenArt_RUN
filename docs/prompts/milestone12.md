# Milestone 12 prompt – smarter pod AI, furniture overhaul, ground levels, library audit

Paste this into a new Claude Code session on the new branch (a copy of `opus_branch_05`).

---

Read `CLAUDE.md` first, then `docs/plan.md`, `docs/progress.md`, `docs/milestone11.md` (§18–§20 and §19.8,
real03) and `docs/gpu-log.md`. Tell me where you run (cloud or Mac) before anything else. Today's date: <fill in>.

## Why this milestone

The pipeline now reads whole floors (real02, real03), but the results are not good enough to show anyone:

1. **Ground and levels**: the agents do not understand elevation differences of the ground: level marks (KOT
   ±0.00, -0.45, +0.15 ...), entrance steps and ramps, a sloping site, a ground floor above or below the street,
   basements. Buildings float, sink or stand on flat ground that the drawings say is not flat.
2. **Furniture is terrible**: pieces are put randomly all over the room. The AI must understand which furniture
   goes with what (a sofa faces the TV with the coffee table between them; chairs stand around their dining table;
   a bed has its headboard on a wall with a nightstand on each side; a desk has its chair; a kitchen is a counter
   run with sink, hob and fridge in a working order; bathrooms follow real layouts) and keep walkways, doors and
   windows free. Untyped drawn pieces still show up as white boxes.
3. **The AI in the pod must be much smarter.** This is the most important point. Today it reaches only a few of 55
   rooms, accepts 4 edits and rejects 73, and does not plan.
4. **The library**: I see furniture and decor that look unrealistic or do not exist as real products, wrong sizes,
   wrong categories. We need a full check of the whole library, and when the library is not good enough the AI must
   say so and suggest what to add.

## Step 0 – diagnosis (no code changes, report first)

Using the committed results (`results/*/real02`, `results/*/real03`, the agent logs `results/agent/<p>/log.md`,
`overrides.json`, the plausibility findings, the renders and contact sheets) and the code (`wenart/agent/`,
`wenart/furniture/`, `wenart/blender/site.py`, `wenart/sheets/`, `assets/`, `wenart/furniture/catalog*.json`):

- List, with evidence (file, view, piece id), every way furniture goes wrong today: random placement, groups broken
  apart, wrong facing, blocked doors and windows, white boxes, wrong scale, pieces in rooms that never hold them.
- Explain why the agent edits get rejected (73 of 77 in real03 run 3) and why it covers so few rooms.
- Explain what the pipeline knows today about ground and floor levels, where level marks are read, and where that
  information is lost.
- Explain how the library is built, how many models and decor items it has per type and per style, and what is
  checked about them today.
- Write it to `docs/milestone12.md` §1 and give me a short report (tables, simple English).

## Step 1 – design (for my OK before building)

Write the design into `docs/milestone12.md` with numbered decisions (D1, D2, ...) and the options you considered.
At least:

**A. Ground and levels**
- Read every level mark (plans, sections, site plans, KOT texts and blocks) into the building JSON with evidence;
  floor elevations per room where they differ (a sunken living room, a raised entrance); the ground level per side
  of the building and at each outside door.
- Infer what the documents leave out (CLAUDE.md evidence rules): steps or a ramp where a door is above the ground,
  a terrain that follows the marks, a plinth; every inferred item marked `inferred` and listed.
- Code checks: no door opens into the air or into the ground, no floor below the terrain without a basement, the
  exterior views show it. The agent gets tools to read and correct levels (validated, logged).

**B. Furniture overhaul**
- Replace random placement with a group-based layout: a room's program (from its type, size, doors, windows and
  the brief) becomes functional groups (seating group, dining group, sleeping group, work group, kitchen run,
  bathroom set ...), each with its anchor piece, partners, relative positions, facing rules, clearances and
  walkways; the groups are placed by a deterministic solver with scores (wall use, sight lines, circulation, door
  swings, daylight), and the VLM only chooses the program, the style and between solver candidates. Look at what
  open-source room-layout work exists (verify papers, repositories and licences; never invent them) and say what
  we reuse.
- Drawn furniture stays the anchor (CLAUDE.md furniture rules); completion adds the missing group partners, never
  a random extra piece.
- No unexplained boxes: every drawn piece is typed (rules, vision, the agent) or recorded as not furniture.
- Code checks for every group rule; a render-side check that pieces stand on the floor, face their group and
  match their real size.

**C. A smarter AI in the pod**
- Re-evaluate the agent model: the strongest open-weight vision-language model that fits the pod (RTX PRO 6000,
  96 GB; verify model ids, sizes, licences and vLLM support from official sources), and whether to split roles
  (a planner model, a vision critic, code checks).
- A plan per room with a checklist (program, groups, findings), budget-aware coverage of every room (cheap code
  checks first, the vision model where it adds something), memory of what failed and why, self-checks before an
  edit is sent, and fewer rejected edits by design (tools that work on groups, not single coordinates).
- Measure it: accepted/rejected edits, rooms covered, findings before/after, time per room.

**D. Library audit and growth**
- A full audit job on the pod: every model, decor item and texture rendered as a thumbnail with a scale reference;
  code checks (real dimensions against the size table, pivot and up axis, mesh and texture errors, duplicates,
  licence fields) and a vision check (is it what its type says, does it look like a real product, which styles it
  fits). Output: a table per item with keep / fix / remove and the reason, and a contact sheet per type.
- Nothing is deleted without my OK (CLAUDE.md).
- Gap report: what each room type and style needs for good groups and what the library lacks; suggestions to add,
  only open-licence sources that allow commercial use (verify each source and licence), with download size, and
  nothing downloaded without my OK. During a run the AI writes "library gap" findings instead of using a wrong
  piece.

**E. Tests and pods**
- CPU tests for every rule; GPU tests for the renders. Pods: real02, real03, real01 and one synthetic project,
  before/after contact sheets, the audit report. Estimate the GPU cost per step first.

## Rules

- All hard rules of `CLAUDE.md` stay: GPU limits, one pod at a time, self-stopping pods, `scripts/gpu_run.py`,
  secrets, evidence and logging, open-weight models and open-source tools only.
- **Budget**: the project total is about $89 of the $100 budget. Give me the GPU cost estimate of this milestone
  with the design and wait for my OK before going over $100 in total.
- Ask me before: any limit, deleting data or library items, a new Network Volume, a single action over $5.
- Commit and push after each step; update `docs/progress.md`; before ending a session check that no pod runs.
- Communication: simple English, short reports, tables for comparisons. Stop after Step 0 and after Step 1 for my
  answers.
