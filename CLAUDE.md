# WenArt_RUN – rules for every Claude session

Read this file first in every session. Keep it short and current.

## What this project is
A proof of concept (PoC): a fully automated pipeline that turns an architectural
project folder (PDF / DWG / photos + style prompt) into photoreal, textured renders
of the furnished rooms, using open-weight AI models and open-source tools only.
Plan: `docs/plan.md`. Status: `docs/progress.md`. GPU spending: `docs/gpu-log.md`.

## Where you run (check first, tell the user)
- If `CLAUDE_CODE_REMOTE=true`: cloud session. No GPU, limited disk, internet only
  through an HTTPS proxy with an allow-list. Reach RunPod pods by HTTPS only
  (no SSH). The pod clones this repo at the current commit.
- Otherwise: the user's Mac. Reach pods over SSH + rsync. Keep the Mac awake.
- CPU work (parsing, validation, unit tests) runs where you are.
- GPU work (model inference, Cycles renders, AI polish, GPU tests, fine-tuning)
  always goes to RunPod through `scripts/gpu_run.py`. Never build Mac-GPU variants.
- If a domain is blocked by the proxy, tell the user exactly which domain to add
  (the list is in `docs/setup.md`, step 4.1).
- RunPod API: use REST v2 `https://api.runpod.io/v2` (v1 retires 15 Nov 2026).
  Pods: image `runpod/pytorch:1.4.0-cu1281-torch291-ubuntu2404`, Network Volume in EU-RO-1,
  GPU: the fastest one in stock under $5.00/h with ≥ 24 GB (order in `scripts/gpu_run.py` GPU_PRIORITY: RTX PRO
  6000, RTX 5090, RTX PRO 5000, L40S, H200/H100, RTX 4090, …, RTX PRO 4500; never L4), prices read live from
  `/v2/catalog/gpus`; a pod whose worst case is over $5 needs your OK first (`--over-5-ok`). Real prices since
  9 Oct 2026: RTX PRO 6000 ≈ $2.5/h (not the $2.09 of early October), RTX 5090 ≈ $1.2/h (32 GB: cannot host the
  52 GB agent/judge server). Plan pods with these numbers.

## Secrets
- `RUNPOD_API_KEY` comes from the environment (cloud) or the user's local store (Mac).
- Pods get the Hugging Face token as `HF_TOKEN={{ RUNPOD_SECRET_hf_token }}`.
- Never print, log, echo, or commit any key or token. Never ask the user to paste
  a key into the chat. `.env` is git-ignored.

## GPU limits (hard rules)
- Max $5.00 per GPU-hour (raised from $1.00 on 3 Oct 2026), max $30 per day (raised from $10 to $30 on 4 Oct 2026; $40 on 9 Oct 2026 only, user OK, `DAY_LIMITS` in `scripts/gpu_run.py`), max 4 hours per pod run (raised from 2 h on 11 Oct 2026, user OK), one pod at a time. 11 Oct 2026 only: the real04 test may pass the USD limits (user OK; day cap $60 in `DAY_LIMITS`, `--over-5-ok`). 27 Oct 2026 (user OK): a pod run may take up to 180 min with `--over-5-ok` (worst case about $7.50), and that day's cap is $45 (`DAY_LIMITS`). 28 Oct 2026 (user OK): the real04 run may take up to 240 min with `--over-5-ok` (worst case about $10), and that day's cap is $50 (`DAY_LIMITS`). 29 Oct 2026 (user OK: "there should not be a limit at 180 min for real06 if 240 is needed than 240 will be given"): the real06 run may take up to 240 min with `--over-5-ok` (worst case about $10); the day cap stays $30. Project total: $500 (raised from $100 on 10 Oct 2026, from $200 on 12 Oct 2026 and from $300 on 27 Oct 2026, user OK; Milestone 13; the
  Milestone 13 pods of `docs/milestone13.md` §8 are approved under that decision, each with `--over-5-ok`; so are
  the three final pods P6 of real04 (with an interior-sky A/B), real03 and real02, user OK of 22 Oct 2026).
  A pod may have 2 GPUs when the price per GPU-hour stays within the limit; its worst case counts as one action
  (user OK of 10 Oct 2026, Milestone 12).
- Ask the user before: going over any limit, creating or deleting a Network Volume,
  deleting any data, or any single action costing more than $5.
- Every pod must shut itself down when its job ends or at the max runtime
  (watchdog inside the pod, `runpodctl pod stop $RUNPOD_POD_ID` or REST fallback, see `scripts/pod_entry.sh`). Never rely on
  the session to stop a pod. If a job fails or hangs: stop the pod first, then debug.
- Before ending a session, check that no pod is running.
- Log every run in `docs/gpu-log.md`: pod ID, GPU, minutes, cost, purpose.
- Models download on the pod into the container-disk cache (`HF_HOME=/opt/wenart/hf`, ≈ 1.1 GB/s;
  the Network Volume is too slow for caches and venvs, plan §5), never here.
- Batch GPU work: several tests per pod session, not one pod per small check.

## Furniture rules
- Fixed equipment drawn in the documents (stairs, kitchen counter runs, kitchen island and appliances, sanitary
  ware) is treated like walls: same type, position, orientation and footprint as drawn. Style changes only the
  look. The AI may fix only a clear drawing or reading error, logged as `adjusted_by_ai` with the reason and the
  plan crop: a front that faces the wall, a misread size (then the size of a real product of that type), a piece
  through a wall or in a door swing (a move of at most 0.5 m) (user OK of 10 Oct 2026, Milestone 12). A drawn
  bathtub or shower a few cm (up to 5 cm) longer than its bay is a misread size: it is shrunk to the nearest real
  product size that fits, `drawn_footprint` kept (user OK of 22 Oct 2026).
- Drawn furniture is kept by default. The AI may correct its orientation, snap it to a wall, change its size to a
  real product size, change its type within the room type's types, and fix clear drawing errors (a rug outline
  read as a piece, a cushion read as a sofa, a table footprint that includes its chairs). Every change keeps
  `drawn_type`, `drawn_footprint`, `drawn_front_deg`, `drawn_height` and is labelled `adjusted_by_ai` with the
  reason. A drawn piece is removed only when it is clearly not furniture (logged with the plan crop as evidence).
  With `keep` or `furnished_rooms_keep_size` only the look, the orientation and clear errors change.
- Footprint clear but type unclear → the AI infers the type from size, room and neighbours, marks it `inferred`
  and lists it in the report. It never stays an unexplained box.
- Rooms with drawn furniture: with `furnished_rooms: complete` (default) the AI adds the pieces the room type
  misses (`added_by_ai`, `completes_room: true`); never a second anchor piece. Small decor if the brief allows it
  (default: yes).
- Rooms with no furniture in the documents: the AI furnishes them in the project style (default).
- Rooms are furnished in functional groups (seating, dining, sleeping, work, kitchen run, bathroom set …) placed by
  the deterministic solver; the AI chooses the program; the code score chooses between solver candidates unless a
  measured test shows the vision model ranks marked candidate images better; the AI never gives coordinates and
  never judges a bare top-down image (user OK of 12 Oct 2026, Milestone 13). No untyped piece is built: it is
  typed, recorded as not furniture, or listed for review.
- An untyped drawn footprint is typed by code first: the same footprint in the twin room or on another level
  (within 1 cm), the block name, or the room's missing group member of that size (`inferred`, with the evidence);
  the AI types the rest from the plan crop (user OK of 12 Oct 2026). Code may also retype a drawn piece that the
  vision models typed when its size, room and neighbours clearly say otherwise (e.g. a nightstand-size "lamp" at a
  bed head becomes that bed's nightstand), labelled `adjusted_by_ai` (by code) with `drawn_type` and the plan crop
  kept (user OK of 22 Oct 2026).
- A drawn furniture size outside its type's product range (a block with its neighbours, a split artefact) is
  snapped to the nearest real product size before the fit (`adjusted_by_ai`, `drawn_footprint` kept, plan crop as
  evidence). A drawn group (a table with its chairs, a sofa with its armchairs and coffee table, a bed with its
  nightstands) is one unit: when its anchor is missing, misread or fails the checks, the solver re-places the group
  around the drawn anchor centre; every member moves at most 0.5 m from its drawn centre and is logged
  `adjusted_by_ai`. A drawn piece that cannot be built is never an obstacle for its own group. With `keep` or
  `furnished_rooms_keep_size` the snap and the group re-solve are off (user OK of 12 Oct 2026).
- Every placement or edit passes the code checks before it is accepted: inside the room, no collisions, real
  clearances and walkways, door swings free, windows free, backs to walls where the type needs it, fronts facing
  their group.
- Every piece is labelled `from_documents` (with evidence), `added_by_ai` or `adjusted_by_ai` (with the reason).

## Library rules (user OK of 10 Oct 2026, Milestone 12; extended with user OK of 12 Oct 2026, Milestone 13)
- Only audited library models (`keep`, `fix`) and audited module or parametric families are used. Every catalogue
  entry carries `licence`, `licence_url`, `licence_declared_by` (`publisher` | `uploader`), `licence_flag` (`none`
  | `non_commercial` | `share_alike` | `no_derivatives` | `research_only` | `regional` | `tool_nc`),
  `commercial_safe` and `attribution`.
- User decision of 24 Oct 2026: every project, every pod run, may use any library model; licences are no selection
  criterion, the look of the renders is (models that fit together and carry the style). So `relaxed` is the default
  (`wenart/defaults.yaml`, `LICENCE_MODE_DEFAULT`). `library.licence_mode: commercial` in a brief (or env
  `WENART_LICENCE_MODE`) still restricts a run to `commercial_safe: yes` entries. `relaxed` may also use
  non-commercial, share-alike, research-only, regional and
  `tool_nc` assets (HSSD under CC BY-NC 4.0 with the user's acceptance of its terms; the TRELLIS.2 models exported
  with the non-commercial tool nvdiffrast stay usable with the `tool_nc` flag until the export is replaced).
  No-derivatives assets are never used. Research-only data sets that forbid redistribution (3D-FUTURE, 3D-FRONT)
  are not used. Paid packs (Maxtree) and BlenderKit are on hold.
- Every render carries `commercial-safe: yes|no` with the flagged asset ids; every run writes `ATTRIBUTION.md`
  (tools and generators, assets with authors and changes, PoC-only assets with the reason, dataset notices).
  Switching back to `commercial` re-runs the fit and the renders without the flagged assets; nothing on the volume
  is deleted.
- Nothing is deleted from the volume without the user's OK. When no audited model fits a drawn anchor, the run
  still builds it, in this order: the nearest audited model within the caps, a module builder with real proportions
  (wardrobe runs, long tables, L-sofas from modules, kitchen runs), the parametric family; it writes a `library gap`
  finding naming what was used. A drawn anchor is never left out and never built as a grey box; the fallback must
  look like a real product (PBR materials, real module sizes), and the report lists every piece built below the
  library level so the gap can be closed (user OK of 12 Oct 2026: "yes, but we need a good model").
- Vegetation and site (user OK of 12 Oct 2026): a row of ≥ 5 drawn tree symbols of equal radius ≤ 0.6 m at a pitch
  ≤ 1.5 × their diameter is a hedge; single symbols are trees; tree height follows the crown radius by size class
  (a crown under 1.5 m is a shrub). Every tree, shrub, hedge and lawn is a real model or generated geometry with
  leaf textures, never a primitive; species not named in the documents are `inferred` and named in the report.
  Terraces, pools and parking get one level each with retaining edges; pools get coping and water; the sky, the sun
  and the horizon are always in the image. Vegetation and site assets are audited like furniture.

## Evidence and inference rules (user OK of 9 Oct 2026, Milestone 11)
- Source geometry (DWG/DXF entities, vector PDF paths) is the anchor for walls, openings, room outlines and
  levels. The AI may override it only for a clear error (e.g. a 5 cm gap in an outer wall, a duplicated wall, a
  door off its wall); it logs the reason and the evidence, and the item is marked `corrected_by_ai`.
- Level marks (KOT texts, blocks and attributes) are source data for floor levels, door thresholds and the ground,
  with the same trust order as geometry; steps, ramps, plinth and terrain are inferred from them where not drawn.
- Trust order when sources disagree: vector geometry > OCR text and dimensions > AI vision. Conflicts: prefer
  DWG > vector PDF > scan > photo, and list every conflict in the report.
- Where the documents are silent, unclear or illogical, the AI infers, completes and corrects: furniture type,
  orientation and placement, missing exterior parts (roof, ground, site), cameras, materials, lighting. Each such
  item is marked `inferred` (or `adjusted_by_ai`) and listed in the report.
- Missing scale or open outer walls: the AI tries to infer them first (dimension text, door widths, stair treads,
  typical room sizes, closing small gaps) and marks them `inferred`. "needs review" only for real blockers: no
  usable geometry at all, or inferences that contradict each other.
- Every wall, door, window, room, furniture piece, label and dimension in the building JSON carries evidence:
  file, page, layer/entity id or pixel box, method (vector / ocr / ai / inferred), confidence; AI changes also
  carry the model, the round and the reason.
- AI calls: temperature 0, typed tools and strict JSON schemas. Every AI edit is checked by code before it is
  accepted. A critique loop with code validation replaces the "two passes must agree" rule; two independent passes
  stay only where no code check exists (e.g. reading a label that no geometry confirms).
- Everything is logged: every check, finding, edit, rejected edit and reason goes to
  `outputs/<p>/orchestrator/log.json` and `log.md` with before/after images. Nothing changes silently.
- An agent edit is accepted only when the finding it targets is gone in the dry re-check and no new critical finding
  appears; "edits accepted" is no success metric, "findings removed" is. Exception `critical_cleared`: when all
  critical targets of a step are gone (measured by code), its major targets may stay if none gets worse (user OK of
  23 Oct 2026). Building-wide edits (roof, terrain, site, exterior cameras) come only from the building session (user
  OK of 12 Oct 2026).
- AI polish must not change geometry: compare edge and depth maps before/after and reject changed results. A
  final vision check compares every render with the building JSON and the source plan; its findings go back to
  the stage that caused them.
- Save a debug image per page with detected elements drawn over the original, colored by method and confidence.

## Engineering conventions
- Open-weight models and open-source tools only; library models of any licence by default (`licence_mode: relaxed`,
  user decision of 24 Oct 2026), flagged in the catalogue, in `docs/plan.md` and in `ATTRIBUTION.md`. GPL
  tools (Blender and its add-ons, LibreDWG, Infinigen's GPL submodule) run as installed programs; no GPL code is
  copied into this repository.
- Cameras keep the Milestone 11 policy (18 mm / 16 mm lenses, 1.25 m) in Milestone 13 (user decision of 12 Oct
  2026); exterior views of long, low buildings may use a wider or tilted framing (user OK of 22 Oct 2026); AI
  polish stays off in Milestone 13; the interior sky is windows-only, +3.5 stops, by default (user decision of 23 Oct
  2026).
- Verify model IDs, versions and flags against official sources; never invent them.
- Before / after (user rule of 25 Oct 2026, replaces the Milestone 13 rule of 24 Oct 2026): every before / after
  compares a run with the project's latest run before it, never a milestone run (`wenart.report.latest`, the default
  of `wenart.report sheets13` / `metrics13`; `--baseline m13` only when asked). After the report the new run becomes
  the latest (`python -m wenart.report latest --out <run>/final/<p> --promote`, committed in `results/baseline/latest/`).
- Tests: CPU tests run here (`pytest -m "not gpu"`); GPU tests run on RunPod
  (`pytest -m gpu` via the runner). Run GPU tests before calling a milestone done.
- Scripts: `#!/usr/bin/env bash`, `set -Eeuo pipefail`, error trap, logs in
  `/workspace/logs/`, idempotent, everything persistent under `/workspace`.
- After every milestone: commit, push, update `docs/progress.md`.
- Communication: simple English, short reports, tables for comparisons.
- Every fix is general: a rule of the pipeline for every project; the project that showed the problem is only the
  test case (user rule of 26 Oct 2026: "fix should be general ... don't ever forget that").
- The architect carries out the safe default fix of every open point that has one, and the next safe fix when one
  cannot be done (`by: architect`, logged, drawn values kept). The AI architect answers the rest (a refused pick is
  asked again with the reason), looks at each floor of the model after the first build, may change a default or
  decide on its own from typed actions; code keeps a decision only when nothing new breaks (user request of 26 Oct
  2026: "let it take decisions more"). The AI inspector asks the visitor checks Q1-Q9 (doors, working heights,
  falls, rooms that make sense, matching pieces, door and window style, rain water, entrances) of every render and
  reports what it fixed and what is left (`orchestrator/inspector.md`) before the user looks (user request of 26 Oct
  2026).
- Argus, the auditor (`wenart/audit`, user requests of 26 Oct 2026), checks everything a run makes, not only the
  looks: nothing lost between stages, every source item used, every warning read, the house can be walked through,
  the renders against the plans, the checkers against each other, the run and the agent themselves. Argus AI
  (open-weight agent model, thinking off, a time budget per look) triages every finding and fixes what it can itself:
  the agent's edit tools in its own session of every round, the code lines' exact fixes, architect decisions; every
  edit passes the same code checks. Every finding has a problem kind; a kind that recurs
  (`results/argus/problem_log.json`) gets a general rule. Review every run with
  `python -m wenart.audit run --results runs/<job>/results --project <p> --log`.
- Every new request or correction of the user becomes a lesson (`python -m wenart.agent.lessons add "..."`,
  `wenart/blender/architect_lessons.json`); the architect checks the lessons on every project (user request of 25 Oct
  2026).
- Today's date for this project: see the user's prompt (planning started 1 Oct 2026).
