# Milestone 12, track A: agent in the pod, run orchestration, model bake-off

Branch `worktree-agent-a012278d51ea14891` (not pushed). Scope: docs/milestone12.md §5 (D16–D20) and the A rows of
§13. CPU only: no pod was started, no model was downloaded. `opus_branch_06` (tracks B, S, L) is merged in
(no conflict); the lead notes of 10 Oct 2026 for track A are done: decor sync after every accepted edit and in
`agent apply`, scene checks and the build manifest's summary in the critic, `furniture[].library_gap` as `LG`,
unknown / unfitted pieces not built (`decor.piece_is_built`), `FIT_CODE` with the size table, dotted keys in the
setup, audit-removed models marked in `ATTRIBUTION.md`, the `levels` tool and the level tools on track L's code.

## 1. As built

### 1.1 Room brief (§5.2, `wenart/agent/brief.py`)

| What | Where | Notes |
|---|---|---|
| The brief | `brief.py: room_brief(building, room_id, *, findings, memory, image_of, allowed_fn, program_fn, members_fn, group_checks_fn, solver_fn, k=3)` | room, conventions, built pieces (type, source, size, front never null with `front_inferred`, lock state, `move_left_m`, group), `not_built`, program, groups with missing partners and their G-checks, room checks, free wall spans, findings split into `fixable` (with the tools allowed for the target) and `not_yours` (with the reason), memory summary, solver top-3 candidates with images, notes when another track's function failed |
| Lock state | `allowed_of`, `allowed_fallback`, `normalise_allowed`, `compact_allowed`, `is_allowed` | track G's `edit_ops.allowed_edits` when it answers, else the CLAUDE.md rules (fixed equipment: `set_front`, `fix_fixture` 0.5 m, `swap_model`; drawn: move <= 0.3 m, wall snap <= 1.2 m, no remove, `mark_not_furniture`; AI pieces free; unbuilt: nothing) |
| Built or not | `built` -> `topdown.is_built` | track S's `decor.piece_is_built` when present, else the same rule: `build` not false, not `unknown`, not a library gap (`asset.method == "none"`) |
| Fixable vs not yours | `classify`, `CHECK_TOOLS`, `NOT_YOURS_REASON` | relayout only for an AI piece or a G/F5 check; G4 and G6 also offer `move_piece` / `set_front` (a nightstand at the foot, a chair turned away) |
| Free wall spans | `free_wall_spans` | doors +-0.1 m kept clear, pieces within 0.15 m occupy, window parts "only below the sill", ids `room:s{i}.{k}` |
| Ranking weight | `fixable_weight`, `findings_of_room` | critical 9, major 3 x max(1, area) |

Unbuilt pieces are never drawn (`topdown.built_pieces`) and never in the vision critic's id list
(`critic_vision.room_ids`), fixing B5.

### 1.2 Tools (§5.3, `wenart/agent/tools.py`, `overrides.py`)

| What | Where |
|---|---|
| Group and room tools: `move_group`, `complete_group`, `place_group`, `relayout_room` (`candidate` 1-3), `set_front`, `retype_piece`, `mark_not_furniture`, `fix_fixture` | `overrides.FURNITURE_TOOLS`, `GROUP_OPS`, `tools.furniture_handler`, `resolve_edit` (`OP_FALLBACK` while track G's ops are stubs: set_front -> rotate, retype_piece -> change_type, mark_not_furniture -> remove) |
| Level tools: `set_mark_kind`, `set_room_floor`, `set_ground_point`, `set_entrance`, `set_terrain` | `overrides.LEVEL_TOOLS`, `tools.level_handler` (track L's `levels.edits.apply_level_edit`, `LEVEL_EDIT_SCHEMAS`), replayed by `overrides.apply(level_edit=...)` |
| `levels` read tool | `tools.t_levels`: levels, marks with kind and use (`LEVEL_MARK_FIELDS`, AI labels), room floors with source and evidence, thresholds, ground (points, surface, source, terrain override, light wells), terrain, entrances (`ENTRANCE_FIELDS`), plinth, `level_inference`, level conflicts, L-findings with their numbers (`levels.checks.check_levels`) |
| `dry_run` (free: no try, no memory, logged as `dry_run`) | `tools.dry_run_handler` |
| `report_library_gap` | `tools.t_report_library_gap` -> `agent_overrides.library_gaps` |
| Failed checks with numbers on every edit | `tools._building_edit` -> `room_checks_now` |
| Decor follows its host after every accepted edit and in `python -m wenart.agent apply` | `tools._building_edit` (`ToolContext.sync_fn`), `overrides.apply(sync=...)`, `overrides.sync_decor` -> `decor.sync_to_hosts` |
| Memory refusal: an identical rejected edit is refused without a model call | `tools.Registry.call` with `memory.Memory.repeat_of` (`refused_by_memory`) |

### 1.3 Loop (§5.4, `wenart/agent/loop.py`, `memory.py`, `prompts.py`)

- Plan first: `AgentLoop.make_plan` (JSON plan, `prompts.PLAN_SCHEMA`) checked by `check_plan` against the brief
  (offered tool, fixable finding, built target, allowed for the target, a tool of the finding); the checked steps or
  `default_checklist` drive the session (`plan_session`: one edit per piece per reply, ends when the checklist is
  done, `finish` or the per-room budget).
- Memory: `memory.Memory` -> `orchestrator/memory.json` (visits, accepted, rejected with why, candidates tried,
  open steps, plans; `edit_key` ignores the reason, rounds numbers to 3 decimals).
- Coverage: `AgentLoop.sessions_for` ranks rooms by (visits, -weight, id); `offered_tools(registry, brief)`.
- Parallel sessions: `workers` (the server's sequences, 4-8) with thread-local `SessionState`, a time cap per
  round (`ROUND_CAP_S` 900), `CallBudget`.
- Vision only where useful: `critic_vision.critique_room(..., looks=True)`: up to 3 previews + plan crop for the
  look checks (`ROOM_LOOK_CHECKS`), code findings given as context, duplicates by family (`RELATED`).
- Code critic: `critic_code.run` adds group (G), level (L), scene (S) families, `LG` library gaps and, from the
  build manifest's furniture summary, `decor_not_rested` (minor S5 on the host) and `scene_checks_failed`
  (critical S5 when no S5 file was read); `scene_summary` in its output. Scene checks are read from
  `outputs/<p>/scene/checks/scene_<level>.json` (where the build writes them) or `build/checks` (the contract's
  path), `critic_code.scene_checks_dir`.
- Time budget from round 0 (B6): `run/stages.est_final_measured(views, previews_s, preview_views, ...)`,
  used by `scheduler.final_estimate` when round 0 was measured (real03: 1372 s estimated vs 1302 s measured; old
  formula 2063 s).
- B8: the loop docstring says "time cap", no "= 40".

### 1.4 Metrics (§5.5, `wenart/agent/metrics.py`)

`metrics.compute(log, memory, since_seq, since_call)`, `write(project_out)` -> `orchestrator/metrics.json`
(accepted / rejected by reason, rooms visited / fixable / fixed, calls, plans ok, minutes, findings before /
after); `python -m wenart.agent metrics [--compare results/compare/<p>/agent_metrics.md --label ...]`; report
section `wenart/report/agent.py: metrics_lines`. Baselines committed: `results/compare/real03/agent_metrics.md`
(M11 run 3: 5 of 78 accepted, 11 of 35 rooms, 144 calls, 10.75 min) and `results/compare/real02/agent_metrics.md`
(G2d: 20 of 197, 312 calls).

### 1.5 Run (`wenart/run/`)

- `scheduler.ProjectRun`: one agent server session per orchestrated run (`open_agent_session`): the layout stage
  (`stages.layout(..., url, key)`) and the decor questions (`stages.decor_ask`) use the agent model; Qwen is the
  fallback when the agent server fails (`_agent_error`, not retried); round 0 measured (`previews_s`, `views`,
  `build_s`), `workers = seqs(agent_key)`.
- `servers.model_entry` (dotted keys `bakeoff.<name>`), `gpu_count()` (`WENART_GPU_COUNT`), `serve_command(...,
  tensor_parallel)`, `VLMServer.devices` (`CUDA_VISIBLE_DEVICES`), a 2-GPU model refused with `ServerError("config")`
  on a 1-GPU pod; `plan._table` skips the nested bake-off table.
- Stage code lists after the merge of B, S, L (the import closures, `tests/test_run_stages.py`): `FIT_CODE` +
  `wenart/furniture/sizes.py`, `wenart/recognition/size_table.yaml`; `LEVELS_CODE` (`wenart/levels/**`,
  `wenart/blender/**`, `canonical.py`, `views.py`, `style/**`, `catalog.py`, `sizes.py`, the catalogues) added to
  sheets / pipeline / pipeline_final, layout, decor and decor_ask (track L's level inference runs in the pipeline
  and imports the site and shell helpers); `GATE_CODE` + `wenart/levels/**`; `AGENT_CODE` + `wenart/levels/**`.
  The plan of real01 before its answers counts 17 views (25 before): its rooms with only `unknown` pieces now count
  as unfurnished (`camsearch.shown_pieces` uses track S's built rule), `tests/test_run_plan.py` updated.
- `copy.audit_removed`: `ATTRIBUTION.md` marks a model the library audit removed, with its reasons (it stays
  credited: older thumbnails show it).
- `scripts/pod_setup_polish.sh: vlm_entries` downloads dotted `AGENT_MODELS` keys (`bakeoff.fp8`), for P1 and for
  track B's P3 (`AUDIT_MODEL_KEY`).
- vLLM stays 0.30.0 (decision below).

### 1.6 Bake-off P1 (§5.1, `wenart/agent/bakeoff.py`)

| Part | Where |
|---|---|
| Task set | `tests/fixtures/m12_bakeoff/tasks.json` (labels, seeds) -> `bakeoff.build` -> `items.json` + `images/` (130 images, 5.3 MB, deterministic) |
| Planted problems (code truth) | `problems_of` (bed_reversed G5, tv_away G1, nightstand_at_foot G4, door_blocked F7, chair_away G6), `plant_options` (an edit that adds exactly its problem), `plant`, `room_pool`, `pick_rooms` |
| Prompts, schemas | `prompt_of`, `schema_of`, `messages_of` (strict JSON, temperature 0) |
| Scoring | `score_item`, `judge_call` (T5: valid, allowed, in plan), `aggregate` (accuracy, false findings, recall, T5 rates, s/call, tokens), T1-T4 score = mean of the four accuracies |
| Runner | `run_model` (server pinned to its GPU(s), every variant, VRAM peak per GPU with `PeakSampler`, a Cycles render of the committed real02 scene next to the server during the first variant, GPU tests on the live server), `run_variant` (8 at a time, time cap, `run_order`) |
| Decision | `decide`: the best single-GPU row, a 2-GPU row only when >= 10 points better on T1-T4; eligible = >= 90 % answered and >= 80 % valid tool calls; ties (1 point) -> fewer s/call |
| Output | `results/bakeoff_m12/<name>.json`, `<name>-<variant>.json`, `summary.json`, `summary.md` |
| Models | `check.yaml models.bakeoff`: fp8 (off/on), bf16 (off/on), muse (low/high), flash_next TP2 (off/on), step_flash TP2 fallback (off); flags verified (see §2) |
| Job | `scripts/jobs/bakeoff_m12.sh` |

## 2. Decisions

| Decision | Why |
|---|---|
| Keep vLLM 0.30.0 | Every flag of the five models exists in v0.30.0 (tool parsers `qwen3_coder`, `muse_glimmer`, `step3p5`; reasoning parsers; `--attention-config.indexer_kv_dtype`, `--moe-backend marlin`). Flash-Next's card asks for commit d4d703c or newer, whose engine-argument set is a strict subset of v0.30.0's (so older than 0.30.0). The recipe calls it "nightly required": the job retries a 2-GPU model once on vLLM 0.31.0 (own venv, built in the background) only if it does not start, and reports it; nothing is adopted without the lead. |
| Variants | Qwen3.8 thinks by default (`chat_template_kwargs.enable_thinking`): off (the M11 setting) and on; Muse Glimmer has no thinking switch, only `reasoning_strength` (low / high). A variant sets the critic's and the planner's thinking together. |
| TP2 instead of TP4 for Step-3.7-Flash | the pod has 2 GPUs; NVFP4 weights (129 GB) fit 2 x 96 GB at 0.85. |
| `--gpu 'RTX PRO 6000'` for P1 | NVFP4 needs Blackwell, the 2-GPU models need 2 x 96 GB. |
| T2/T3 truth from code | the five problems are measured by `problems_of` on the image the model gets; a room's own problems (real02 bedrooms have nightstands at the bed foot) are part of the truth, and the clean layout of T3 has the fewest. |
| T1 crops from the committed debug plans | the same image the agent's `plan_crop` gives; the prompt says the coloured labels are earlier guesses. 5 real03 items whose crop was too blurry to judge were replaced by clear ones (a stove, beds, a shower, an armchair). |
| T4 `null` labels | not scored where the image does not settle it (the low-poly table lamp on a pole, the slab-like throw). |
| Time cap 720 s per variant | keeps the job inside 100 minutes with phase C last; items not started count as wrong and the row needs >= 90 % answered. |
| Scene checks path | the build writes to `outputs/<p>/scene/checks`; the contract says `build/checks`; both are read. |

## 3. Tests

| File | Tests | What |
|---|---|---|
| `tests/test_agent_brief.py` | 7 | brief contents, lock states, fixable / not yours, spans, candidates, unbuilt pieces |
| `tests/test_agent_memory.py` | 5 | memory file, edit keys, refusal of a repeated rejected edit |
| `tests/test_agent_loop_m12.py` | 12 | plan-first sessions, checked plans, coverage ranking, parallel sessions, time cap, decor sync, level edits, op fallbacks, critic families |
| `tests/test_agent_metrics.py` | 3 | metrics, compare table |
| `tests/test_agent_scene_inputs.py` | 4 | built rule (unknown, library gap), scene checks folder, manifest summary findings, the `levels` tool on track L's inference and the level tools' schemas |
| `tests/test_bakeoff_m12.py` | 16 | models = contract ids and revisions, variants, dotted downloads, task set, planted-problem checks, scoring, decision rule, scripted runs (T1-T5), time cap, summary, crop, job script, partial rebuild, `run_model` files |
| `tests/test_run_agent_m12.py` | 5 | agent session for layout + decor, fallback, round-0 estimate, workers, 2-GPU serving |
| changed: `tests/test_agent_loop.py`, `test_agent_tools.py`, `test_run_agent.py`, `test_run_copy.py` (+1) | | M12 semantics, one agent session, audit mark in `ATTRIBUTION.md` |
| GPU: `tests/gpu/test_agent.py` | +1 | every bake-off task answers on the served model (run by P1 against `bakeoff.fp8`) |

Last run (10 Oct 2026, after the merge of B, S, L): `pytest -m "not gpu"` on the 31 agent, bake-off, run, copy, stage, job and contract test files: 401 passed, 11 skipped. GPU tests: run by P1.

## 4. The bake-off task set

| Task | Items | Truth | Content |
|---|---|---|---|
| T1 | 40 | hand labels, one-line reason each (`tasks.json`) | real03 18 (12 not furniture: door arcs, room numbers, a sign, lift doors, a double door, a level mark, a door leaf, boxes along a door swing and across a bedroom; 6 pieces: counters, a stove, a bed, a toilet, a chair), real02 22 (palms, armchairs, tables, a cabinet, a stool, a stove, a sink, a nightstand, a desk, wardrobes, sofa, beds, washbasin, showers) |
| T2 | 30 rooms | `problems_of` on the planted building | 9 projects; planted: 19 rooms with 1, 5 with 2, 6 with none; truth items: nightstand 12, door 10, chair 8, bed 7, TV 4 |
| T3 | 20 rooms x 3 layouts | the clean layout (positions 1/2/3: 7/6/7) | one defect layout with 1 plant, one with up to 2 |
| T4 | 20 views | hand labels (null = not scored) | floating/sunk decor: 12 yes, 6 no, 2 null; wrong object: 3 yes, 12 no, 5 null |
| T5 | 20 briefs | the brief's lock state and the checked plan | the planted T2 rooms with >= 1 plant; findings G1/G4/G5/G6/F7 |

Rebuild: `python -m wenart.agent.bakeoff build [--tasks T5]` (a partial rebuild keeps the other tasks' items).
After track G is merged, rebuilding T5 gives briefs with groups, program and candidates (now notes only).

## 5. P1: the exact command

```
python3 scripts/gpu_run.py run --job scripts/jobs/bakeoff_m12.sh --gpu-count 2 --gpu 'RTX PRO 6000' --disk 500 \
  --max-minutes 100 --over-5-ok --purpose "M12 P1: agent model bake-off (5 tasks, 5 models, 9 variants)"
```

Expected about 75 minutes (setup with downloads 6, phase A fp8 + muse at once 25 incl. the GPU tests, phase B bf16
19, phase C flash_next 22, summary 1); the deadline (`WENART_DEADLINE` = start + 85 min) stops the last phase and
the watchdog stops the pod at 100 minutes. 2 x RTX PRO 6000 at about $2.5/h each: about $6.2 expected, $8.3 at
most. Disk: 408 GB of models + 2 vLLM venvs. Results: `$RESULTS/bakeoff_m12/` (copied after every step).
`BAKEOFF_CAP_S` (720), `BAKEOFF_VLLM_RETRY` (0.31.0, empty = off) and `RENDER_SCENE` can be set with `--env`.

## 6. What is left

- Run P1 (lead) and record the pick; then set `check.yaml models.agent` (and its variant's thinking) to the pick.
- After the merge: rebuild T5 (`--tasks T5`) so the briefs carry track G's groups, program and candidates; the
  room tools `relayout_room` / `place_group` / `complete_group` / `move_group` only work once track G's ops exist.
- The orchestrated run's GPU tests (`tests/gpu/test_run_*`) were not touched; the next full run (P5+) checks the
  agent with the new brief end to end.

## 7. Requests to other tracks

| Track | File | Request |
|---|---|---|
| G | `wenart/furniture/edit_ops.py` | ops (and `EDIT_SCHEMAS`) for `set_front`, `retype_piece`, `mark_not_furniture`, `move_group`, `complete_group`, `place_group`, `relayout_room` (argument `candidate`: int 1-3, the solver's rank); `allowed_edits(building, piece)` keyed by tool or op name, values `{allowed, why, move_left_m}` |
| G | `wenart/furniture/layout.py` | it already sends `enable_thinking: false`; if P1 picks Muse Glimmer (no thinking switch), also send the model's template keys (`check.yaml models.<key>.variants.<v>.template`, e.g. `reasoning_strength: low`) |
| G | `group_checks`, `solver` | violations in the M11 format; `solve_room(building, room_id, k)` candidates with `rank`, `score`, `group_violations`; `apply_candidate(building, room_id, candidate)` |
| S | `wenart/furniture/decor_ai.py` | the same as layout.py if P1 picks Muse Glimmer (`enable_thinking: false` is sent already) |
| L | `wenart/levels/edits.py`, `checks.py` | none: `LEVEL_EDIT_SCHEMAS`, `apply_level_edit(building, edit)` and `check_levels(building, scene_manifest, render_manifest)` are used as merged |
| lead | `docs/milestone12.md` §13.3 | scene checks live in `outputs/<p>/scene/checks/` (the build's `--out`); the agent reads both |
| S / L (owner of `wenart/blender/build.py`, `render.py`) | exterior camera plans / render manifest | L7 needs `visible_objects` on the exterior cameras (at least the entrance objects `steps_<door>` / `ramp_<door>` in view); track A writes no render manifest. Until then L7 checks only that an exterior view sees the entrance door (`visible_openings`) |
| lead | `tests/test_run_agent.py` expectations | one agent server session per run now serves layout, decor questions and the agent (`servers.starts == ["agent"]`); Qwen only as fallback |
