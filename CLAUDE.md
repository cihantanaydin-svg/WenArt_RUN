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
  default GPU RTX A5000 (then RTX 4090, RTX A6000), prices read live from `/v2/catalog/gpus`.

## Secrets
- `RUNPOD_API_KEY` comes from the environment (cloud) or the user's local store (Mac).
- Pods get the Hugging Face token as `HF_TOKEN={{ RUNPOD_SECRET_hf_token }}`.
- Never print, log, echo, or commit any key or token. Never ask the user to paste
  a key into the chat. `.env` is git-ignored.

## GPU limits (hard rules)
- Max $1.00 per GPU-hour, max $10 per day, max 2 hours per pod run, one pod at a time.
- Ask the user before: going over any limit, creating or deleting a Network Volume,
  deleting any data, or any single action costing more than $5.
- Every pod must shut itself down when its job ends or at the max runtime
  (watchdog inside the pod, `runpodctl pod stop $RUNPOD_POD_ID` or REST fallback, see `scripts/pod_entry.sh`). Never rely on
  the session to stop a pod. If a job fails or hangs: stop the pod first, then debug.
- Before ending a session, check that no pod is running.
- Log every run in `docs/gpu-log.md`: pod ID, GPU, minutes, cost, purpose.
- Models download on the pod into the Network Volume (`HF_HOME=/workspace/hf`), never here.
- Batch GPU work: several tests per pod session, not one pod per small check.

## Furniture rules
- Furniture and fixed equipment drawn in the documents are treated like walls:
  same type, position, orientation and footprint size as drawn. Style changes only
  the look (materials, colors, design details).
- Footprint clear but type unclear → keep the footprint, mark `unverified`, show it
  in debug images. Never guess silently.
- Rooms that have furniture in the documents: never add, remove or move furniture.
  Small decor (cushions, plants, books) only if the brief allows it (default: yes).
- Rooms with no furniture in the documents: furnish with AI in the project style
  (default), with real clearances; never block doors or windows.
- Every piece is labelled `from_documents` (with evidence) or `added_by_ai`.

## No-hallucination rules
- Trust order: vector geometry (DXF entities, PDF paths) > OCR text and dimensions
  > AI vision suggestions. AI proposes; checks against the source decide.
- Every wall, door, window, room, furniture piece, label and dimension in the
  building JSON carries evidence: file, page, layer/entity id or pixel box,
  method (vector / ocr / ai) and confidence.
- Unverifiable items are marked `unverified` and listed in the report. Nothing is
  silently added, completed or "fixed". Missing scale or no closed outer walls →
  stop that project with a `needs review` report.
- Cross-check dimension text vs measured lengths, area labels vs computed areas,
  element counts across documents, outline across floors. Conflicts: prefer
  DWG > vector PDF > scan > photo, and list every conflict in the report.
- AI calls: temperature 0, strict JSON-schema validation, two independent passes;
  keep only what agrees or matches source evidence.
- Creative AI only where documents are silent: materials, colors, lighting mood,
  decor, furniture for empty rooms.
- AI polish must not change geometry: compare edge and depth maps before/after and
  reject changed results. A final vision check compares every render with the
  building JSON and the source plan and lists mismatches.
- Save a debug image per page with detected elements drawn over the original,
  colored by method and confidence.

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
