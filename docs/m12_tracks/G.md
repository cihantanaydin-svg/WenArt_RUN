# Milestone 12 – track G (groups): functional groups, the deterministic solver, group checks, group edits

Design: `docs/milestone12.md` §1.2, §1.4, §2, §4.2–§4.6, §4.9 (D8–D12, D15), §5.2–§5.3 (D17–D18 tools), §13
(contracts). Session: cloud, CPU only, 10 Oct 2026. Branch `worktree-agent-af9ba22abf5edbaba`, merged with
`opus_branch_06` (tracks B, S, L).

## As built

### 1. Groups as data – `wenart/furniture/groups.yaml` (new), `wenart/furniture/groups.py`

| What | Where |
|---|---|
| 13 groups: seating, dining, sleeping_double, sleeping_single, storage, work, living_storage, kitchen_run, island, bathroom_set, wc_set, entrance, balcony. Per group: `layout` (anchored / set / run), room types, priority, anchor (types, place wall/free, alignment, size rows by room area), options (e.g. `sofa_2_armchairs`, `bed_nightstands`, `seats_6`, run shapes I/L/U/galley), partners (place `facing_wall`, `front`, `flank`, `beside_head`, `foot`, `around`, `chair`, `stools`, `pair`), set members, the kitchen run's modules and order | `groups.yaml` `groups:` |
| 21 rules, each with its sources (NKBA kitchen and bath, ADA/ADM M4, DIN 18011, Panero, viewing distance, "ours" for flagged assumptions): walkway 0.60 (rec 0.75), main walkway 0.80 (0.91), kitchen aisle 0.90 (1.07), landings sink 0.46 / hob 0.30 / fridge 0.38 (or ≤ 1.22 m across, or the run turning the corner within 0.10 m), triangle legs 1.2–2.7 m, sum ≤ 7.9 m, diner pull-out 0.81 (0.91 / 1.12), fixture front 0.53 (0.76), toilet side 0.38, bed sides 0.60 (0.75), coffee gap 0.30 (0.35–0.45), TV ≥ 1.50 m (rec 1.2–1.6 × screen), TV axis 0.30 m / 10°, armchair facing 30°, nightstand gap ≤ 0.30 m (rec 0.05), storage front 0.80, desk back 0.80, window band 0.30 m deep | `groups.yaml` `rules:`, `sources:` |
| Soft-term weights (Merrell 2011 / Yu 2011 names: wall_use, sight_tv, bed_sees_door, desk_side_light, daylight, circulation, seating_crossed, related_near, balance, drawn_distance, recommended, partners, sink_window); use zones per type (front / back / sides / foot, by rule name) | `groups.yaml` `weights:`, `use_zones:` |
| Loading with a strict JSON schema plus cross checks (unknown types, rules, sources, options, run order); a broken YAML is refused with the place | `groups.validate_config`, `config`, `load_groups`, `rule`, `rule_min`, `rule_rec`, `weights`, `use_zone`, `sizes_for` |
| Group membership of a room: the pieces' `group` tags first, then template matching (anchors in id order, partners nearest first); `missing` partner types per group | `groups.group_members`, `match_groups`, `_expected_missing` |
| Built pieces (track S request): `piece_is_built` = not `build: false`, not `unknown`, not a library gap (`asset.method == "none"`); the same rule as `decor.piece_is_built` (a test keeps them equal) | `groups.piece_is_built`, `NOT_BUILT_ASSET_METHODS` |
| Milestone 11 `place_group` / `GROUPS` kept for `add_group` | `groups.place_group` |

### 2. The room program – `wenart/furniture/program.py`

| What | Where |
|---|---|
| `room_program(building, room_id, brief=None, choices=None)`: a rule table per room type and zone (living: seating by area, dining ≥ 18 m² without a dining room, living storage; bedroom: double / single (child subtype) bed, storage, work ≥ 12 m²; kitchen run (+ island, dining by area); bathroom / wc sets; hall entrance by width; other: work; balcony: table and 2 chairs); zones of open kitchens get their kind's groups | `program.room_program`, `_rows` |
| Drawn pieces first: every matched drawn group replaces the program's row (priority + 100), keeps its drawn members and lists only its `missing` partners; never a second anchor of the room; an unverified anchor and a group of another room type ("no completion") get nothing; an unknown drawn piece with the size of a missing anchor blocks that anchor (no second bed beside an unknown 1.6 × 2.0 box) | `program.room_program`, `_may_be` |
| `choices` (group id → option) pick an option (the VLM's or the agent's) | `program.room_program` |

### 3. The solver – `wenart/furniture/solver.py`

| What | Where |
|---|---|
| Free space: a 5 cm raster in the room's main-axis frame, integral images for O(1) box tests, layers per type (doors, swings, window bands by height), arithmetic box footprints for quarter turns, exact shapely tests near other pieces | `group_checks.RoomRaster`, `Space`, `Layer`, `Space.box_fp`, `Space.exact_ok` |
| Anchor candidates every 0.10 m along each wall from both ends and on a 0.10 m grid for free anchors (only inside the group's zone), size rows by area, ordered by a cheap pre-score with an early stop; partners placed with a small search in the anchor's frame; use zones kept free; walkway connectivity on the raster (doors 0.60, main path 0.80 from the entrance, every new use zone reached) | `anchored_candidates`, `_wall_positions`, `_free_positions`, `_partners`, `member_candidates`, `run_candidates` (`Leg`, `Path`, galley), `Walk` |
| Beam search width 32 with 4 children per parent first (diversity), skip transitions, required / optional bonuses, a node budget, deterministic tie-breaks (score, then signatures) | `_search`, `BEAM_WIDTH`, `PER_PARENT`, `NODE_BUDGET` |
| Final verification on the building: placer geometry of every new piece plus every new critical / major group finding (G14 aside) is a hard failure; a layout that fails only by some groups is tried without them (a fridge without a landing beside a drawn run); top-k diverse in the main group first, then in any group; failed candidates only fill up to k | `solve_room`, `verify`, `_failing_levels`, `_without` |
| Drawn pieces are fixed; their free use zones (a drawn bed's sides, a drawn table's pull-out) are reserved at the root; a drawn anchor gets the partners that fit (a TV without a wall does not block the coffee table); `fixed_ids` keep added pieces and their groups | `fixed_zones`, `_fixed_items`, `_partners` (`new_anchor`) |
| Candidate: `rank, score, terms, pieces, groups, hard_failures, group_violations, options, placed, not_placed, kept_ids, nodes`; pieces `added_by_ai`, `method: rule`, `group {group_id, group, role, anchor_id}`, `layout {against_wall, solver_role, option}` | `_candidate`, `_piece_dict` |
| `apply_candidate`: the room's replaceable added pieces out (and their decor), the candidate's in with fresh ids, anchors remapped | `apply_candidate` |

### 4. Group checks – `wenart/furniture/group_checks.py`; plausibility uses them

| What | Where |
|---|---|
| G1 TV opposite the sofa (axis, facing, distance), G2 coffee table off the sofa front inside the corridor, G3 armchairs face the group, G4 a nightstand per free side at the head (gap ≤ 0.30 m), G5 headboard on a wall / sides / foot, G6 chairs by table size, facing, pull-out from the table edge, G7 desk chair and room behind, G8 kitchen order, landings (NKBA: beside, across ≤ 1.22 m, corner), hob off windows, triangle, aisle, G9 sink / hob / fridge, G10 bathroom fixtures and clearances, G11 walkways (doors connected, main path from the entrance, every use zone reached), G12 nothing taller than sill + 0.05 m within 0.30 m of a window (a TV unit counts 1.30 m), G13 room in front of wardrobes and door-fronted storage, G14 types the room / zone never holds. Every message names its numbers | `check_room`, `check_building`, `check_view`, `_g1_g3`, `_g4_g5`, `_g6` … `_g14` |
| Only built pieces are judged (`groups.piece_is_built`) | `RoomView.floor` |
| Plausibility: F5 counting replaced by G1–G13 (G14 is the critic's), F6 for seats and cribs only, F7 without the window part (G12), F1 zone-aware, F2 flags a piece turned 90° against its product sizes (real02 `f_L0_007`); library gaps not built | `plausibility._f5`, `_f2`, `oriented_fit`, `size_range`, `GROUP_CHECKS` |

### 5. The layout stage – `wenart/furniture/layout.py`, `wenart/furniture/prompts.py`

| What | Where |
|---|---|
| Per empty room: program → solver top 3 → the vision model picks one: a multimodal request with one labelled top-down image per candidate, its groups, options, score and terms, temperature 0, strict JSON `{candidate, reason}`; one candidate, an invalid or failed answer: candidate 1 (logged); `LayoutClient.down` after the first transport error (later rooms are not asked) | `layout_room`, `choose_candidate`, `LayoutClient.choose`, `prompts.choice_prompt`, `choice_schema`, `CHOICE_SYSTEM_PROMPT` |
| Added pieces: solver evidence first, the choice's last (`ai` with the model, or `derived`), `checks`, `layout.candidate/score`; a room without a usable candidate stays empty with the reason ("nothing fits: …", "nothing missing: …") | `apply_choice`, `layout_room` |
| Partners (twins, `same_as`): copied / mirrored; a copy that would lose a piece is not used, the room is solved itself | `furnish_building`, `_copy_layout` |
| CLI unchanged (`--passes` accepted and ignored); no exit 3 any more (a dead server costs one call); `layout.json` (with `solve_s`, `vision_model_down`), `layout_report.md`, per room `<room>.json`, `<room>.png` (candidates side by side), `<room>_c<k>.png` (what the model saw); `--no-orchestrator` runs call the same `main` | `main`, `write_room_debug`, `layout_report` |

### 6. Completion of furnished rooms – `wenart/furniture/complete.py`

| What | Where |
|---|---|
| The same flow with the drawn pieces fixed: only the partners a drawn group misses, the missing members of a drawn set, a fridge beside a drawn run (with a landing), and the groups the room type misses whole; `added_by_ai`, `completes_room: true`, `method: rule`; wall cabinets by rule as before | `complete_room`, `add_wall_cabinets` |
| Drawn anchors and partners tagged `group {group_id, group, role, anchor_id}` (track S/fit request; not a locked key) | `tag_drawn_groups` |
| Partners: mapped copies keep their group (id with this room's id, anchor mapped onto this room's drawn piece); a copy that fails a check or a partner that does not map → completed itself, with the reason | `copy_room`, `copy_added`, `_map_group`, `complete_building` |
| `completion.json` keeps the mode and kept rooms (`locked.keep_rooms_of`), each room's program, candidates, choice, added pieces, `missing`, `drawn_layout`; `completion_report.md`; debug PNG + JSON per room | `summary`, `report`, `RoomCompletion.to_dict`, `write_room_debug` |

### 7. Edits of the agent – `wenart/furniture/edit_ops.py`, `wenart/furniture/locked.py`

| Tool | Rule |
|---|---|
| `place_group(room_id, group, option?)` | the solver places a missing group with the room's other pieces fixed; never a second anchor of the room; only a group of the room type |
| `complete_group(group_id)` | the group's missing partners (refused when nothing is missing, naming the members) |
| `move_group(group_id, span_id, offset?)` | a group of added pieces solved again on a free wall span (`free_spans`: outline edges minus doors ± 0.10 m and built pieces against them); partners follow; drawn groups refused |
| `relayout_room(room_id, candidate?, choices?)` | the room solved again with the program choices, candidate k (1–5) |
| `add(type)` without a place | a missing partner of a group goes through the solver (Milestone 11 put a nightstand 0.78 m from the bed) |
| `retype_piece(piece_id, type)` | only types of the room / zone at the piece that fit its footprint, never turned against a drawn front; the refusal lists the candidates |
| `mark_not_furniture(piece_id, kind, evidence)` | `build: false` + a `symbols[]` entry (`former_piece_id`, crop); new findings reported, not held against it |
| `fix_fixture(piece_id, size?, center?)` (U1) | drawn fixed equipment > 30 % outside its real range → the nearest real size (from its wall line); through a wall or in a door swing → the nearest valid spot ≤ 0.5 m; `locked.check` accepts exactly that |
| `set_front(piece_id, front_deg)` | a drawn piece without a front gets one along a side (± 1°), the same rectangle |
| `resize` | a size turned 90° against the type (a bed 2.0 wide, 1.6 deep) is refused (F2 rule) |
| `dry_run(edit)` | the answer with `building: None`, `dry_run: true` |
| `allowed_edits(building, piece_id)` | per tool `{allowed, why, move_left_m}` from the CLAUDE.md locks (fixed equipment, kept rooms, drawn move allowance left, groups) |
| Acceptance | group tools: placer checks + no new critical / major finding; others: placer checks + the score does not drop; walkways are G11's (`placer.check_all(walkways=False)`), not the 0.9 m erosion |

### 8. Smaller changes

`schemas.ALLOWED_TYPES["balcony"]` (new row) and `["other"]` + `office_chair` (the work group's chair at its desk);
`placer.check_all(..., walkways=True)`; `tests/gpu/test_furnish.py` and `test_m10_completion.py` read the solver
flow (checked offline on real02 outputs with a fake chooser: 8 passed, 1 skipped).

## Decisions

| Decision | Why |
|---|---|
| Minimums hard, recommended values only score | the sources give both; hard recommended values left small rooms empty |
| Pull-out measured from the table edge (0.81 m) | NKBA / Panero measure from the table edge; chairs stand inside it |
| Nightstand gap ≤ 0.30 m (rec 0.05) | 0.10 m failed common drawings; beyond 0.30 m it no longer reads as the bed's |
| Fridge landing across (≤ 1.22 m) or round the corner | NKBA allows both; a drawn run that fills its wall otherwise never gets a fridge |
| A drawn anchor gets the partners that fit | its required TV may have no wall; the coffee table should still come |
| A partner copy that would lose a piece is not used | a whole group beats the same look in both twins (real02 balcony and twin rooms) |
| Group tools accepted on "no new critical / major" | a group may bring minor findings (an armchair a few degrees off); the solver's own hard rule |
| `mark_not_furniture` not held to the score | leaving out a misread symbol may expose a real gap (a bathroom without a toilet), which is a finding, not a reason to keep the symbol |
| Unknown drawn boxes stay obstacles for the solver | they are drawn symbols; giant misread boxes are track R's to split or type |
| `place_group` of the Milestone 11 templates kept | `add_group` and its tests; the new tools use the solver |
| The M11 contract test allows the M12 ops after the M11 ones | §13.2 extends `EDIT_OPS` |

## Tests added / rewritten

- `tests/test_group_checks.py` (15): pass and fail per G-check with the numbers, unbuilt pieces not judged, NKBA
  fridge landing across, use zones.
- `tests/test_solver_rooms.py` (10): candidate format, determinism, rectangle, L room, two doors, drawn anchors kept,
  completion adds only missing partners, fixed ids, kitchen order, time per room.
- `tests/test_groups_program.py` (16 with parameters): YAML validation and refusals, rule table, drawn groups first,
  unverified and unknown anchors, foreign groups, choices.
- `tests/test_groups_edits.py` (13): every new tool pass / fail, `dry_run`, `allowed_edits`, U1 and the locked check,
  "resize never turns a bed" and "add a partner through the solver" (both fail on Milestone 11 code).
- Rewritten: `tests/test_layout.py` (22), `tests/test_complete.py` (35 incl. parameters 44); updated:
  `test_plausibility.py`, `test_groups.py`, `test_vllm_schemas.py`, `test_complete_placer.py`, `test_m11_contracts.py`,
  `tests/gpu/test_furnish.py`, `tests/gpu/test_m10_completion.py`.

## Before → after (real02, real03)

Before: `results/furniture/<p>/building_furnished.json` (Milestone 11 layout + completion). After: this branch's
layout stage on `building_fitted.json`, no vision model (the solver's best). Both measured with the same checks.

| real02 | before | after | | real03 | before | after |
|---|---|---|---|---|---|---|
| G major (all checks) | 102 | **62** | | G major | 98 | **68** |
| G minor | 24 | 20 | | G minor | 7 | 12 |
| G1 major (TV) | 2 | 0 | | G1 major | 5 | 0 |
| G3 major (armchairs) | 6 | 2 | | G2 major | 3 | 0 |
| G4 major (nightstands) | 8 | 0 | | G4 major | 4 | 0 |
| G6 major (dining) | 8 | 2 | | G5 major (beds, drawn) | 10 | 7 |
| G11 major (walkways) | 23 | 7 | | G11 major | 10 | 8 |
| G12 major (windows) | 8 | 6 | | G12 major | 15 | 6 |
| G10 major (bathrooms, drawn) | 18 | 18 | | G10 major | 29 | 28 |
| F4 major | 20 | 10 | | F4 major | 27 | 17 |
| F8 major | 6 | 2 | | F8 major | 2 | 1 |
| mean plausibility score | 57.5 | **67.3** | | mean score | 62.5 | **67.6** |
| rooms with a hard failure in the best candidate | – | 0 | | | – | 0 |
| solver s per room (mean / median / max, shared CPU) | – | 0.34 / 0.36 / 0.57 | | | – | 0.29 / 0.16 / 1.99 |

What stays is drawn: bathrooms (G10), beds (G5), drawn kitchens without a hob (G8/G9), F2/F3/F9 of drawn pieces and
real03's misread boxes (giant diagonal unknowns over whole rooms) — the agent's `fix_fixture`, `retype_piece`,
`mark_not_furniture` and track R's reading.

## What is left

- GPU tests on a pod (`pytest -m gpu tests/gpu/test_furnish.py tests/gpu/test_m10_completion.py`) with the real vision
  model; the choice prompt and images are untested against Qwen3-VL here.
- real03: most bedrooms and living rooms "nothing fits" because unknown boxes cover the floor (track R).
- `move_group` takes span ids from `edit_ops.free_spans`; the room brief (track A) should list them.

## Changes needed in other tracks' files

- **Track A** (`wenart/run/stages.py`): the `layout`, `decor`, `decor_ask`, `fit`, `refit`, `sheets`, `pipeline`,
  `pipeline_final` code lists must add `wenart/furniture/groups.py`, `groups.yaml`, `group_checks.py`,
  `program.py`, `solver.py` (and track B's `sizes.py`, `catalog.py`); `tests/test_run_stages.py::
  test_code_lists_cover_the_import_closure` fails on `opus_branch_06` already (sheets → `wenart.levels.model` →
  `wenart.blender`). `critic_code.FAMILY_OF` needs G1–G14. The agent's tools: map the new ops (`TOOL_OPS` names), call
  `dry_run` / `allowed_edits` / `free_spans` for the room brief; `relayout_room` takes `candidate` / `choices`.
- **Track B**: the size table's crib orientation (a crib drawn 1.36 × 0.7 reads as turned).
- **Track R**: split / type the giant unknown boxes (real03), toilets read 1.145 × 0.356 m (U1 at ingest; the agent
  can use `fix_fixture` meanwhile), sanitary ware through walls.
- **Lead / vision check** (`tests/test_vision_check_prompts.py::test_decoy_type_first_allowed_absent_then_fallback`):
  balcony now has allowed types (`table_dining`, `chair`, `bench`), so `decoy_type("balcony", {"armchair"}, …)` is
  `table_dining`, not the fallback `desk`; the assertion should use a room type without a row (e.g. `"shaft"`).
- **Schema** (lead): `furniture.group` carries `anchor_id` too (allowed, not listed); `adjusted_by_ai.fix_fixture`
  and `adjusted_by_ai.not_furniture` are new keys of the existing object.
