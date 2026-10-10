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
  `/v2/catalog/gpus`; a pod whose worst case is over $5 needs your OK first (`--over-5-ok`).

## Secrets
- `RUNPOD_API_KEY` comes from the environment (cloud) or the user's local store (Mac).
- Pods get the Hugging Face token as `HF_TOKEN={{ RUNPOD_SECRET_hf_token }}`.
- Never print, log, echo, or commit any key or token. Never ask the user to paste
  a key into the chat. `.env` is git-ignored.

## GPU limits (hard rules)
- Max $5.00 per GPU-hour (raised from $1.00 on 3 Oct 2026), max $30 per day (raised from $10 to $30 on 4 Oct 2026; $40 on 9 Oct 2026 only, user OK, `DAY_LIMITS` in `scripts/gpu_run.py`), max 2 hours per pod run, one pod at a time. Project total: $200 (raised from $100 on 10 Oct 2026, user OK).
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
  look. The AI may fix only a clear drawing error (e.g. a front that faces the wall), logged as `adjusted_by_ai`.
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
- Every placement or edit passes the code checks before it is accepted: inside the room, no collisions, real
  clearances and walkways, door swings free, windows free, backs to walls where the type needs it, fronts facing
  their group.
- Every piece is labelled `from_documents` (with evidence), `added_by_ai` or `adjusted_by_ai` (with the reason).

## Evidence and inference rules (user OK of 9 Oct 2026, Milestone 11)
- Source geometry (DWG/DXF entities, vector PDF paths) is the anchor for walls, openings, room outlines and
  levels. The AI may override it only for a clear error (e.g. a 5 cm gap in an outer wall, a duplicated wall, a
  door off its wall); it logs the reason and the evidence, and the item is marked `corrected_by_ai`.
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
- AI polish must not change geometry: compare edge and depth maps before/after and reject changed results. A
  final vision check compares every render with the building JSON and the source plan; its findings go back to
  the stage that caused them.
- Save a debug image per page with detected elements drawn over the original, colored by method and confidence.

## Engineering conventions
- Open-weight models and open-source tools only; prefer licenses that allow
  commercial use; flag the rest in `docs/plan.md`.
- Verify model IDs, versions and flags against official sources; never invent them.
- Tests: CPU tests run here (`pytest -m "not gpu"`); GPU tests run on RunPod
  (`pytest -m gpu` via the runner). Run GPU tests before calling a milestone done.
- Scripts: `#!/usr/bin/env bash`, `set -Eeuo pipefail`, error trap, logs in
  `/workspace/logs/`, idempotent, everything persistent under `/workspace`.
- After every milestone: commit, push, update `docs/progress.md`.
- Communication: simple English, short reports, tables for comparisons.
- Today's date for this project: see the user's prompt (planning started 1 Oct 2026).
