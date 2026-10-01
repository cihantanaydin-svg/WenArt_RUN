# Progress

## Milestone 0 – plan (done, waiting for your OK)

What works:
- Repo skeleton, `CLAUDE.md` rules, building JSON schema + validated example.
- `docs/plan.md`: reality check, approach choice (3D-first with gated polish), stage diagram,
  option tables with licences and picks, RunPod setup, cost estimate (~$35–45 of $100).
- `docs/setup.md`: step-by-step setup guide for Hugging Face, RunPod and the cloud environment.

What fails / is blocked:
- This cloud environment blocks `api.runpod.io`, `huggingface.co` and others, so no RunPod
  read-only checks could run yet. Hugging Face model cards could not be fetched; licences were
  verified from GitHub LICENSE files instead and marked (S) where only search snippets exist.
- Live GPU prices are from third-party snippets; the runner will read them from the API.

GPU cost so far: $0.00

## Setup checks (1 Oct 2026, done)

Read-only checks from `docs/setup.md` step 5, all HTTP 200:
- Pods: none running. Network volumes: none (expected before Milestone 1).
- Secret `hf_token`: exists. RunPod key: present as environment variable, read scope works.
- Hugging Face API: reachable. All allow-listed domains reachable except
  `cdn-lfs.huggingface.co` (proxy 502; not needed, models download on the pod).
- Setup script: all CPU tools installed (poppler, tesseract, ezdxf, pdfplumber, shapely, opencv, pytest).
- Live secure-cloud prices (USD/h): RTX A5000 0.27, RTX A6000 0.53, RTX 4090 0.74, A40 0.49, L4 0.49.
  All within the $1.00/h limit; availability was LOW for each.
- Not checkable by API: RunPod balance and auto-top-up setting (please confirm on the billing page).

## Milestone 1 – RunPod runner + pod setup (done, 1 Oct 2026)

What works (tested on a real pod, A40 in CA-MTL-1, 6.7 min, $0.05):
- `scripts/gpu_run.py run --job scripts/jobs/smoke.sh`: live price/stock check, limits
  ($1/h, $10/day, 2 h, one pod), pod create via REST v2, status over the token-protected
  pod HTTP server (`https://<pod>-8000.proxy.runpod.net`), result download, pod logs,
  row in `docs/gpu-log.md`, terminate at the end. Subcommands: `status`, `gpus [--dc]`,
  `volume-create`, `logs`, `stop`, `terminate`, `sweep`.
- `scripts/pod_entry.sh` on the pod: watchdog (max runtime), status server, clone of this
  repo at the pushed commit, setup, job, self-stop after a grace period. Self-stop verified:
  the pod reached EXITED on its own, the runner only terminated it afterwards.
- `scripts/pod_setup.sh`: apt libs, Blender 5.2.2 (sha256 verified, 383 MB), venv with
  `scripts/pod_requirements.txt` on top of the image's torch 2.9.1+cu128. Idempotent.
- GPU smoke tests (`tests/gpu/test_smoke.py`, 4 passed in 9 s): CUDA matmul, /workspace
  writable, Hugging Face download with the `hf_token` secret into `HF_HOME`, Cycles render
  on the GPU with OptiX (`results/smoke/cube.jpg`).
- CPU tests for the runner logic: `pytest -m "not gpu"` (6 passed).

Findings:
- `api.runpod.io` sits behind Cloudflare and bans Python's default user agent; the runner
  sends its own. Pod log events use the key `line`.
- EU-RO-1 had no RTX A5000 / 4090 / A6000 stock today (only RTX PRO 4000, RTX PRO 4500, L4).
  Stock changes hourly; the runner picks live from a priority list.
- vLLM 0.30.0 pins torch 2.13.0, so it gets its own venv in Milestone 2.
- The no-volume run proved the loop, but nothing persisted (Blender and the venv were
  installed on the container disk, ~1 min).

GPU cost so far: $0.05 (plus $16.37 of earlier pod use on the account in September, not ours).

Volume created (1 Oct 2026): `h9er811d55`, 120 GB STANDARD, EU-RO-1. Two smoke runs on it: the
first installed Blender + venv (10 min, $0.10), the second reused them (setup 10 s, $0.05).

## Milestone 2 – recognition (done, 1 Oct 2026)

What works:
- Synthetic test projects with ground truth (`wenart/synthetic`, `docs/synthetic.md`): synthetic-01
  (DXF + vector PDF + scan), synthetic-02 (scan + phone photo), synthetic-03 (3-page PDF + furniture
  DXF with deliberate conflicts). Previews in `results/synthetic/`.
- Vector path (`wenart/ingest`): DXF and vector-PDF extraction, room polygons from walls, openings and
  furniture linked to walls/rooms, cross-checks (dimension vs measured, area label vs computed, counts
  across documents, outline across floors), conflicts, unverified, `needs_review` stop, debug images,
  `report.md`. Reproduces the truth of all three projects (`pytest -m "not gpu"`: 194 passed).
- Recognition bake-off on the pod (`wenart/recognition`, `scripts/jobs/bakeoff.sh`, results in
  `results/bakeoff/`): PaddleOCR vs Tesseract, Qwen3-VL-8B vs GLM-4.6V-Flash via vLLM 0.30, two-pass
  agreement. Numbers:

| Task (3 scan/photo pages) | PaddleOCR | Tesseract | Qwen3-VL-8B (fp8) | GLM-4.6V-Flash (fp8) |
|---|---|---|---|---|
| Page class / level title / scale text | - | - | 100 % | 100 % |
| Room labels (recall) | 73 % | 20 % | 100 % | 100 % |
| All texts (recall / precision) | 65 % / 63 % | 48 % / 35 % | - | - |
| Furniture + door + window symbols (recall) | - | - | 0 % | 1 % |
| Latency per page / call | 0.4 s (18 s with model load) | 0.4 s | 5.1 s | 5.6 s |

What fails / open:
- Symbol detection on the full page is unusable (see `docs/plan.md` §4.2): the drawing is ~20 % of the
  sheet, so symbols are ~15 px after downscaling. Milestone 3 adds crop-to-drawing + per-room tiles.
- LibreDWG 0.13.3 `dxf2dwg` rejects DXFs with DIMENSION blocks ("Invalid DXF code 50 for MTEXT");
  `mobilya_plani.dxf` (no dimensions) round-trips. Try 0.14.1 on the pod next.
- Code review of Milestone 2 (4 lenses, 3 independent verifiers per finding): 24 confirmed findings,
  all fixed with a failing-then-passing test each (`pytest -m "not gpu"`: 220 passed). The important
  ones: furniture drawn only on a separate furniture plan was dropped (now the furniture plan is the
  furniture source of its level), an open outer wall without a label did not stop the project (now a
  loose-end check sets `needs_review`), a known block drawn at another size kept the table size (now the
  drawn size wins and the piece is `unverified` with a conflict), cross-document furniture and room-label
  disagreements were silent (now `unverified` + conflict), the page scale could follow a wrong dimension
  text (now the scale note wins), rotated dimensions were measured wrong, and the bake-off job lost its
  results on a watchdog stop (now copied after every stage).

Lessons (all recorded in `docs/plan.md` §5): the network volume is far too slow for venvs (55 min vs 3 min
on the container disk); model downloads run at 1.1 GB/s on the pod; Blackwell pods need the cu129
PaddlePaddle wheel and `VLLM_USE_FLASHINFER_SAMPLER=0`; 24 GB cards need fp8 + 8192 context for these VLMs.
Four bake-off pod runs were needed (volume stall, stage-trap bug, vLLM memory/sampler); every pod stopped
itself, see `docs/gpu-log.md`.

Verification run after the fixes (L4, 16 min, $0.13): both vLLM servers up in about 2 minutes each,
`tests/gpu/test_recognition.py` vLLM tests green. Open item: PaddleOCR reads 3/5 room labels on the
synthetic-02 scan (SALON and YATAK ODASI are crossed by furniture lines), under the 80 % target of the
spec; the test stays as a strict expected failure with that reason, and both VLMs read 5/5 on the same
page, so the pipeline will take room labels from the VLM pass with OCR as cross-check (Milestone 3).

GPU cost so far: $1.63 (`docs/gpu-log.md` has the exact rows).

## Milestone 3 – 3D shell, materials, lighting, first renders (done, 1 Oct 2026)

What works (`docs/milestone3.md` is the spec):
- `wenart/style`: brief text → deterministic style profile (floor, walls, wet rooms, trim, lighting mood);
  unmatched words are listed, assumed slots are warned, never guessed. `wenart/assets`: CC0 textures and
  HDRIs from Poly Haven and ambientCG with a licence-checked manifest (anything not CC0 is refused).
- `wenart/blender` (Blender 5.2 LTS, headless): walls from centre lines, openings cut with exact booleans
  (centre projected onto the wall line, shift recorded), door frames and leaves, window frames and glass,
  thresholds under doors, floors and ceilings per room, furniture proxies at the drawn footprints with a
  front marker (unverified pieces striped red), PBR materials with box-projected textures in metres and
  albedo normalised to the intended colour (gain recorded), HDRI + sun from the style, three cameras per
  room with a free-point search (never inside a proxy), Cycles passes (RGB, depth, normal, object index,
  multilayer EXR), `scene.blend`, `scene.glb`, `scene_manifest.json` (every object → element id, evidence,
  material, assumed defaults) and `render_manifest.json` (per view: device, seconds, depth range, index
  values, scene fingerprint for resumes).
- Pod job `scripts/jobs/render.sh`: pipeline → style → assets → build → render → GPU tests, resumable,
  results copied after every stage. Final run (RTX PRO 4000): 87 views of synthetic-01 and synthetic-03 at
  1920×1080, 128 samples, 4.4–6.2 s per view with OptiX (8 s on an L4), scene build 30 s per project, whole
  job 16 min, $0.15; `tests/gpu/test_render.py`: 12 passed. Previews: `results/renders/`.
- Recognition follow-ups: `wenart/recognition/tiles.py` (crop to the drawing, 1024 px tiles, merge across
  tiles) and the `--tiled` symbol stage, LibreDWG 0.14.1 first in the pod setup. CPU-tested; the next
  bake-off run measures them on the pod.
- Code review (4 lenses, 3 verifiers per finding): 21 confirmed findings, all fixed with a failing-then-
  passing test (`pytest -m "not gpu"`: 356 passed). The important ones: doors on a wall face were not cut
  through, no floor under doorways, render manifest only written at the end, cameras inside tall proxies,
  the drawing-extent heuristic dropping a plan that fills the sheet, no CC0 check in the scene build.

Open items:
- The white plaster photo shows mottling after the brightness gain; blend with the flat colour (Milestone 5 polish).
- Rooms without documented furniture stay empty; real assets and AI layout are Milestone 4.
- synthetic-02 (scan + photo only) stops at `needs_review` until the recognition path writes a building JSON.
- The pod venv lacked matplotlib, so the DXF debug images were skipped there (added to
  `scripts/pod_requirements.txt`, takes effect on the next pod).

GPU cost so far: $2.07 (`docs/gpu-log.md`).

Next step: Milestone 4: furniture assets fitted to the drawn footprints (Poly Haven, Objaverse CC0/CC-BY,
TRELLIS.2 fallback), AI layout for empty rooms with clearance checks, and the bake-off re-run with the
tiled symbol pass.
