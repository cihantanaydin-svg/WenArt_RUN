# Progress

## Milestone 0 – plan (done, approved 3 Oct 2026)

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

## Milestone 4 – furniture: library assets, parametric fallback, AI layout, decor (done, 2 Oct 2026)

What works (`docs/milestone4.md` is the spec):
- `wenart/furniture/catalog.json`: 31 Poly Haven models (CC0 only, checked against the API) for 13 furniture
  types with measured bounding boxes and frame data; sanitary ware, kitchen blocks, wardrobes, fridges and
  washing machines are parametric by design. `wenart/furniture/fit.py` picks the model whose box aspect is
  closest to the drawn footprint, scales it to the footprint (non-uniform scale ≤ 15 %, mean scale 0.75–1.30,
  else next candidate, else the parametric mesh), never touches the footprint, type, rotation, room or status
  (`FROZEN_KEYS` + byte comparison) and writes a fit report per project. `wenart/assets/models.py` downloads the
  glTF + textures (sha256, licence re-checked) on the pod.
- `wenart/blender/parametric.py`: recognisable meshes for 25 types (bed with headboard and pillows, sofa with
  arms and cushions, wardrobe with doors, kitchen counter with worktop and plinth, toilet, washbasin, shower
  with thin glass panels, ...), box equal to the footprint ± 1 cm, materials from the style.
  `wenart/blender/furniture.py` imports the fitted glTF once per asset (shared materials and packed images),
  re-orients it into the piece frame, scales it and puts it on the footprint; unverified pieces keep the red
  stripes as an overlay on the asset's materials; pass index per piece, decor shares its host's index.
- `wenart/furniture/layout.py` + `placer.py`: for every room without documented furniture, Qwen3-VL-8B is
  asked twice (temperature 0, strict JSON schema with the allowed types and size options of the room type);
  each answer is checked with shapely (inside the room shrunk by 2 cm, no overlap, 0.6 m clearance in front
  of beds/sofas/desks/wardrobes, door approach strips and swing arcs free, a 0.9 m walkway from every door to
  every other door and window, nothing taller than the sill in the window band, against-wall pieces touching
  a wall within 5 cm) and repaired (snap, slide, shrink, relocate, drop; ≤ 40 steps, every step logged). The
  proposal with the fewest dropped pieces wins; pieces both passes agree on get confidence 0.9, others 0.6.
  Anchor first: when the room's anchor piece (bed, sofa, counter, toilet, washbasin) was dropped, it is placed
  alone, locked, and the rest gives way. Types the room type does not allow are rejected before placement.
- `wenart/furniture/decor.py`: cushions on sofas and beds, books on shelves and desks, one potted plant per
  living room or bedroom in a free corner (library plant model, CC0), never on a walkway, a door approach or
  in another piece's clearance; off when the brief says `decor: false`.
- Pod job `scripts/jobs/furnish.sh`: setup → pipeline → style → assets → fit → layout (vLLM server once for
  both projects) → decor → refit → build → render → GPU tests, resumable, results copied after every stage.

Measured (RTX PRO 4000, furnish run 5, 2 Oct 2026, `results/furniture/`, `results/renders/`):

| Item | synthetic-01 | synthetic-03 |
|---|---|---|
| Pieces from the documents | 13 (6 library, 7 parametric) | 21 (9 library, 12 parametric) |
| Empty rooms furnished by AI | 7 rooms, 26 pieces (12 library) | 11 rooms, 32 pieces (17 library) |
| Model time per room (2 passes) | 10.6 s mean | 8.3 s mean |
| Decor (cushions, books, plants) | 16 pieces | 19 pieces |
| Views rendered (128 samples, OptiX) | 30 at 6.7 s | 57 at 5.1 s |
| GPU tests | `test_furnish.py` 8 passed, `test_render.py` 12 passed | |

Whole job 40 min including setup, $0.38. Anchor-first fired in 3 of 36 model passes; no proposed type was
rejected. Five pod runs for this milestone: $1.42 (two failed runs, one stopped early).

Found and fixed on the way (each with a failing-then-passing test):
- Run 1: library models fell back to parametric (resolver looked for `<id>.gltf`, the catalogue has `<id>_1k.gltf`);
  a 1.1 m tall sofa (no uniform-scale limit); bedrooms without a bed (the iteration cap dropped the anchor).
- Run 2: both L1 bedrooms still lost their bed: the small pieces were repaired first and took the floor →
  anchor-first retry. The index pass missed pieces behind the shower glass (Cycles' data passes stop at a
  Glass BSDF) → thin glass (transparent + glossy by Fresnel) for furniture glass.
- Run 3 previews: every library piece rendered with its texture atlas sampled by the box UVs in metres (the
  asset UV layer was active but not the render layer) → `active_render` set, test added.
- Review of the milestone code (10 confirmed findings, all fixed): plants were never built in Blender, camera
  obstacles of library pieces were scaled twice, a door flush with a corner lost its walkway checks, no
  deterministic allowed-type check, inside-room tolerance disagreed with the GPU test, plants in another
  piece's clearance, the catalogue's plant models unused, fallback height inconsistent, swapped width/depth
  turned the piece, log numbering in the retry.

Open items:
- Catalogue coverage: no CC0 wardrobe, kitchen or sanitary models on Poly Haven; coffee tables, TV units,
  dining tables, stoves and desks fail the scale rule for the drawn sizes (the models are too big or small),
  so about half of the pieces are parametric. Objaverse CC0/CC-BY and TRELLIS.2 (plan §4.8) are the next step.
- The "Gothic" bed and commode are the only CC0 bed/dresser models: style-neutral choices are missing.
- Tiled symbol pass: no gain at 150 dpi (GLM 4 → 10 %, Qwen 0 %, one timeout); the fine-tuned detector of
  plan §4.2 stays the path for symbols. LibreDWG 0.14.1 tarball is not downloadable (GNU mirror and GitHub);
  0.13.3 stays (DXF DIMENSION/MTEXT round trip fails there, recorded in `results/bakeoff/dwg_roundtrip.json`).
- Mottled white plaster and dark charcoal rooms: material and lighting polish is Milestone 5.
- Rooms narrower than 0.9 m clear get no walkway requirement (documented relaxation).

GPU cost so far: see `docs/gpu-log.md`.

Next step: Milestone 5: AI polish (image-to-image with depth/edge control, geometry change check), the final
vision check against the building JSON, and real-room photos as style and material references.

## Milestone 5 – Cycles look fixes, gated AI polish, final vision check (done, 2 Oct 2026)

What works (`docs/milestone5.md` is the spec; §13 lists the integration and review decisions):
- Look (`wenart/blender`): window glass seen as glass only by camera and mirror rays (the old shader let 2.4×
  the sun through and gave everything an orange cast), flat albedo for plaster and paint (white walls are
  white, charcoal is charcoal), a light portal per window, per-camera auto exposure and white balance from a
  1/8-resolution metering render (0.35 s per view), uint16 index / depth_mm / normal maps, `render_key` reuse,
  `--hide`/`--plug`/`--hide-sets`/`--look-from` control renders, build fingerprint with `build --reuse`.
  Before / after: `results/renders/<p>/` (the M4 previews are in git history, commit c2656af).
- AI polish (`wenart/polish`): Z-Image-Turbo + Fun ControlNet Union 2.1, img2img with one control image, all
  weights resident (no CPU offload), loaded from local snapshot folders; an attempt ladder where every attempt
  is gated at once, a room rule (the views of one room stay all polished or all Cycles), window panes always
  get the Cycles pixels back, resumable attempts.
- Change gate (`wenart/gate`): lost geometry edges, new straight lines on bare walls/floors, Depth Anything V2
  Small depth after a scale/shift fit, SAM 2.1 masks on both images, CIELAB colour, white-wall chroma, DINOv2
  (logged); calibrated with benign and negative controls (`results/gate/<p>/gate_calibration.md`).
- Final vision check (`wenart/vision_check`): expected elements from the object-index pass, a building-JSON
  cross-check projected with a depth test, a crop of the source plan page per view (camera and view cone
  drawn), Qwen3-VL-8B + GLM-4.6V-Flash with a sentinel decoy, removal / insertion / type-swap controls, realism
  preference; a polished image is dropped when it loses an element or gains a door, window or furniture piece.
- Style reference photos (`wenart/style/photos.py`): both models agree on the vocabulary terms of a room photo
  before a term may fill a slot the brief leaves open; final report per project with contact sheets
  (`results/final/<p>/final_report.md`).

Measured (pod runs 0–2, `docs/gpu-log.md`, M5 total $2.41):

| Item | synthetic-01 | synthetic-03 |
|---|---|---|
| Views (all re-rendered with the new look) | 30 | 57 |
| Exposure range | −1.0 … +7.0 EV | −1.5 … +8.0 EV (4 views at the +8 limit) |
| Polish attempts / mean seconds | 52 / 7.0 s | 135 / 6.4 s |
| Final: polished / Cycles | 24 / 6 (room rule 6) | 20 / 37 (gate 10, room rule 26, check 1) |
| Vision-check mismatches on final images | 2 views (shower enclosure missed by both models, also on Cycles) | 2 in 2 views |
| Realism preference (polished preferred by ≥ 3 of 4 answers) | 0 of 24 | 2 of 20 |

| Calibration | Value |
|---|---|
| Gate: benign controls accepted / negatives rejected | 128/128 / 326/348 (93.7 %; small shifts, scales, rotations 91.5 %) |
| Gate: presumed-bad polishes (strength 0.75, no control) rejected | 8/8 |
| Polish: diffusion speed at 1920×1088 | 2.0 s/forward (RTX 4090), 2.9–3.8 s (RTX PRO 4500); peak 22.5 GiB |
| Vision check: decoys accepted / false extras | 0–2 % / 0 % |
| Vision check: removal flagged / confirmed | 100 % / 62–71 % |
| Vision check: insertion confirmed | 0–14 % (target 60 %, missed: the check is advisory for absolute flags) |
| Vision check: false missing on clean renders | 8–9 % with the start roles, 0 % with the calibrated roles |

Found and fixed on the way (each with a test): the tokenizer did not load offline (transformers asks for a
`tokenizer/config.json` that does not exist; models now load from local snapshot folders), the pod reported
112 host CPUs and numpy/torch oversubscribed the pod's 11-CPU quota (10–50× slower gate), the CPU-offload
fallback would have broken every later attempt (the ControlNet shares the transformer's embedders), window
glass bent the outside view, the cross-check flagged correctly placed furniture, the insertion decoy covered
the inserted element, results were re-copied after every stage (≈ 30 min of I/O), results were downloaded one
file at a time. Review of the milestone: 6 lenses, 2 refuting verifiers per finding, 15 distinct findings
confirmed and fixed (`docs/milestone5.md` §13.1).

Needs your OK (listed in `wenart/gate/thresholds.yaml: calibration.user_ok: pending`):
- The gate limits from run 1a are looser than the start values for edges (global 0.95 → 0.935), depth (0.02 →
  0.05, per region 0.05 → 0.14) and masks (0.90 → 0.62), and tighter for colour, white walls and per-object
  edges. With the start values the gate rejected 12 % of harmless changes (JPEG, noise, blur) and most
  polishes; with the new ones it accepts every harmless change and still rejects 94 % of the deliberate
  geometry and colour changes. Say if you want the stricter start values back.
- The vision check runs as `advisory` for absolute flags because it rarely notices an added, unlisted element
  (insertion 0–14 %); removals, type swaps and the polish decision work.

Open items:
- Polish realism: at the strengths the gate accepts (0.125–0.375) the two judges call polished and Cycles
  images "the same" in 55 of 56 answers on the sweep and prefer only 2 of the 44 final polished images; at 0.5 the polish starts to
  change furniture (a desk drawer disappears) and is rejected. More realism should come from the Cycles side
  (furniture assets, textiles, lamps, contact shadows) or a tile/upscale ControlNet, not from a stronger polish.
- The depth check is the main reason polishes are rejected (41 of 45 rejected attempts in synthetic-03, 10 of 11
  in synthetic-01), mostly in
  halls, storage rooms, the WC and the balcony (large flat surfaces); the room rule then keeps the whole room in
  Cycles. A per-region noise floor measured on the reference (JPEG + noise perturbations in `prepare`) would let
  the gate be strict where depth is stable and tolerant where it is not.
- Windows blow out at interior exposure; 4 dark rooms of synthetic-03 hit the +8 EV limit.
- Some cameras frame mostly bare walls (bathrooms, one child's room view): camera composition (Milestone 3
  code) needs a look.
- The brief "charcoal and white" makes every wall charcoal (the second colour is dropped with a warning);
  Tiles074 is a marble look for "light tiles"; shower panels keep the M4 thin glass.
- Gate thresholds were set on two synthetic projects; real projects should be calibrated again
  (`python -m wenart.gate calibrate`), the cross-check shows they differ per project.

GPU cost so far: $6.13 (`docs/gpu-log.md`).

Next step: Milestone 6: full runs on real projects (your folders in `projects/`), with a gate calibration per
project, and the realism work on the Cycles side.

## Milestone 6 – one-command full runs, Cycles realism, real-project intake (done, 3 Oct 2026)

What works (`docs/milestone6.md` is the spec; §13 lists what changed while running it):
- **One command per pod** (`scripts/jobs/full.sh` → `python -m wenart.run pod`): every stage of every project
  from the project folder to the final report (intake, pipeline, style photos, style, assets, fit, AI layout, decor,
  build, render, controls, gate calibration + validation, polish, vision check, report, GPU tests), batched by GPU
  holder so each vision model starts at most twice per pod; stage records with input fingerprints (a resumed pod
  redoes nothing that is done), deadline-aware stages, `needs_review` as a normal end state, public and private run
  manifests. `python -m wenart.run plan` estimates views, minutes and the pod split on the CPU.
- **Two new test projects**: `synthetic-04` (DXF + vector PDF of the same floor, L-shaped rooms, an armchair at 45°)
  and `synthetic-05` (notched outline, furniture only on a separate furniture plan, en-suite, study, a style photo,
  polish off). Room labels like `EBEVEYN BANYO` and `SALON + MUTFAK` now get the right room type.
- **Cameras**: searched positions (ray-cast score), straight verticals with lens shift, 1–3 views per room by size.
- **Cycles look**: tiled wet walls (wall faces split per room), veneer doors with handles, skirting, soft bedding,
  kitchen fronts that are no longer black, steel that looks like metal, a ceiling light for dim rooms, pulled
  (non-blown) windows, no red cast from the "unverified" stripes. Every added detail is labelled `assumed` in the
  scene manifest; no furniture moved or added.
- **Realism A/B** (`wenart/vision_check/realism.py`): forced choice per aspect, both orders, both models, with
  known-direction and null controls that decide whether the judges can be trusted.
- **Private projects** (`docs/intake.md`): you upload a folder to the network volume with the RunPod S3 API under a
  neutral alias (`real-01`); only an allow-listed summary comes back to this session; nothing goes to GitHub.
  Tested on the pod with a private copy of synthetic-02 (`selftest-02`).
- **Gate per project**: every project with polish on is calibrated and validated before its polish (benign ≥ 95 %
  accepted, negatives ≥ 90 % rejected); a project that fails gets Cycles images only.

Pod runs (RTX PRO 4500, `docs/gpu-log.md`, M6 total **$2.61**):

| Pod | Content | Minutes | Cost | Result |
|---|---|---|---|---|
| A | full run synthetic-01 + synthetic-03 | 82 | $0.99 | ok, GPU tests 74 passed |
| B | full run synthetic-04, -05, -02 + private self-test + A/B renders and controls | 68 | $0.82 | ok, GPU tests 67 passed |
| C | A/B judging (2 models, 1,840 answers) | 47 | $0.56 | exit 1: GLM missed the null-control target (see below) |
| C2 | same, answers reused, stricter signal rule | 20 | $0.24 | ok, GPU tests 7 passed |

| Project | End state | Views | Final: polished / Cycles | Gate validation (benign / negatives) | Views with a final mismatch |
|---|---|---|---|---|---|
| synthetic-01 | ok | 29 | 18 / 11 | ok (0.97 / 0.96) | 2 |
| synthetic-03 | ok | 50 | 36 / 14 | ok (0.98 / 0.99) | 0 |
| synthetic-04 | ok | 14 | 10 / 4 | ok (0.98 / 0.98) | 0 |
| synthetic-05 | ok | 25 | 0 / 25 (polish off by the brief) | – | 3 |
| synthetic-02 | needs review (scan and photo only) | – | – | – | – |
| selftest-02 (private path) | needs review, as expected | – | – | – | – |

Cameras and look, M5 → M6 (same projects):

| | synthetic-01 | synthetic-03 |
|---|---|---|
| Views | 30 → 29 | 57 → 50 |
| Median share of the frame showing furniture | 0.16 → 0.30 | 0.06 → 0.16 |
| Views with < 10 % furniture | 8 → 3 | 32 → 18 |
| Views metered at the +8 EV limit (dark rooms) | 0 → 0 | 4 → 0 |
| Views with > 5 % clipped window pixels | 7 → 0 | 12 → 0 |
| Polished final images | 24 of 30 → 18 of 29 | 20 of 57 → 36 of 50 |

Realism A/B, M5 look vs M6 look on the same 87 M5 cameras (`results/realism/realism_summary.md`):
- Both judges lean clearly to the M6 look: consensus on "photo" 22 wins, 0 losses, 65 ties (per room 16 / 0 / 13);
  Qwen 35 / 1, GLM 48 / 4; deciding cues: light falloff, window light, fewer artefacts, material texture.
- **By the rule fixed before the run this is "not measurable"**: Qwen does not see a lighting-only degradation
  (2 of 8) and picks the first image 87 % of the time; GLM misses the low-sample control (5 of 8) and is not
  reproducible on byte-identical requests (4 of 32 aspects flipped, target ≤ 10 %). Both give one verdict for all
  four aspects (halo ≈ 1.0). So the numbers above are evidence, not a measured result.
- `AgX - Punchy` vs the default look: not measurable either (Qwen always ties; GLM prefers the default look 35 : 8).
- Pod C exited 1 on the GLM determinism test. That measures the judge, not our code; the rule now also needs the
  null controls before a judge counts (stricter; no decision changed) and the GPU test checks that rule.

Found and fixed on the way (each with a test): the judge pod rebuilt the pairs file and dropped the control sets;
stage fingerprints missed imported modules (a fix would not re-run a stage); A/B records decided a project's state;
gate calibration redone on every resume; a failed model download reused forever; a deadline cut hidden by the next
step; result collection reported ok after failed downloads; `--max-bounces 0` made window panes black; old M5
renders and polish files leaking into the new results (pre-M6 output folders are now archived, never deleted);
an L-shaped room's fallback camera outside the room; the report counting views from an old polish manifest.
Review: 6 finders, 6 adversarial verifiers, 19 of 22 findings confirmed and fixed (`docs/milestone6.md` §13).

Needs your OK or action:
- **Real projects**: follow `docs/intake.md` (create a RunPod S3 API key yourself, never paste it into the chat;
  export DXF or vector PDF from your CAD program; upload as `real-01`, `real-02`, …; tell me only the alias).
  Then one pod runs them with `PRIVATE_PROJECTS=real-01`.
- The M5 gate limits (`calibration.user_ok: pending`) are still waiting for your OK; with the M6 look all three
  polished projects pass the new per-project validation.
- The vision check is still advisory for absolute flags (it rarely notices an inserted element).
- `CLAUDE.md` now names the RTX PRO 4500 as the default GPU (then RTX 4090, RTX PRO 4000; never L4); the A5000 has
  had no stock.

Open items:
- Realism judging: ask one aspect per call, balance positions inside the prompt, or use a better judge (or a human
  rating) before the next look change; the current judges cannot certify a look change.
- Library assets ignore the style: Gothic beds and a chesterfield sofa in a Japandi flat; the library single bed is a
  bare metal frame without a mattress.
- Small bathrooms and WCs still give close-up views; empty storage rooms get up to 3 bare views (area rule).
- Vision-check mismatches are mostly shower glass and doors seen edge-on in halls.
- DWG files are not read (users export DXF); scans and phone photos still stop at `needs review`.
- The window pull adds ≈ 1 s per 1080p view; the time rule in `wenart/run/plan.py` does not count it yet.

GPU cost so far: $8.74 (`docs/gpu-log.md`).

Next step: see "Decisions of 3 Oct 2026" below.

## Decisions of 3 Oct 2026

| # | Item | Your decision | What it means |
|---|---|---|---|
| 1 | Plan | approved | `docs/plan.md` is the baseline, with the changes recorded in the milestone specs. |
| 2 | Change-gate limits | keep the calibrated limits | `wenart/gate/thresholds.yaml: calibration.user_ok: "2026-10-03"`; every polished project is still validated first. |
| 3 | Vision check | advisory now, improve later | stays advisory; better detection of added objects is Milestone 7 work. |
| 4 | AI polish | keep it on | review polished vs plain side by side on the first real project, then decide again. |
| 5 | Realism judging | improve the AI protocol | Milestone 7: one aspect per question, balanced image order, then the A/B again (≈ $0.5). |
| 6 | Colour look | switch to `AgX - Punchy` | Milestone 7: new default look (all renders re-render once). |
| 7 | Library furniture | style filter, and a larger library | Milestone 7: library models only when they fit the style (else parametric); drop beds without a mattress; add more CC0/CC-BY models (plan §4.8: Objaverse, TRELLIS.2). |
| 8 | Small/empty rooms | one view for rooms with no furniture | Milestone 7 (small change in `camsearch.py`). |
| 9 | Input formats | DWG **and** scans/photos are needed | Milestone 7: DWG reading (a working converter) and the recognition path for scanned and photographed plans in the pipeline. |
| 10 | Confidentiality | not confidential for now | your projects go into `projects/<name>/` (public repo); the private upload path stays ready. |
| 11 | Repository | stays public | no change. |
| 12 | GPU | faster GPU for faster jobs; GPU-hour limit raised from $1 to $5 | done: the runner picks the fastest GPU in stock under $5/h (RTX PRO 6000 first: 96 GB, same architecture as the PRO 4500, $2.09/h, in stock in EU-RO-1; H100/H200/A100 had no stock there); a pod whose worst case is over $5 needs your OK (`--over-5-ok`, CLAUDE.md rule). The $10/day and 2 h rules stay. |
| 13 | Budget | no milestone cap | no cap per milestone; the `CLAUDE.md` limits ($10/day, $1/h, 2 h per pod, ask before any action over $5) stay. The volume is kept. |

Next step (when you are ready): Milestone 7 with your real project `projects/real01/` (your upload, moved there from
`projects/projects/real01/`), plus items 3, 5, 6, 7, 8 and 9 above.

## Milestone 7 – real projects in (CAD PDF in feet, DWG, scans, photos), style-true furniture, AgX Punchy, better checks (done, 4 Oct 2026)

What works (`docs/milestone7.md` is the spec):
- **Your project `real01`** (AutoCAD PDF, feet and inches, no title, no brief) runs end to end with the same
  command as the synthetic projects. The new generic plan core reads it:
  - scale from the two overall dimensions (50', 30'), confirmed by the 8 room-size labels (12.435 pt/ft);
  - 13 walls from the hatched wall bands (0.150 m and 0.229 m thick);
  - 5 doors, 9 windows, 3 doorless openings, and 1 virtual separator where Drawing Room and Dining share one
    floor area;
  - 9 rooms, including Pooja (prayer room: never furnished by AI), Store and the stair hall;
  - the plot wall, parking and garden recorded under `site` (not built);
  - 20 furniture pieces: the stair (2 flights, built as real steps) and the L-shaped kitchen counter by
    rule, and 16 pieces typed by two AI passes (Qwen3-VL-8B and GLM-4.6V-Flash). 16 of 17 asked pieces are
    right against the reference, with no wrong verified type. The second sofa stays `unknown`: the two
    passes disagreed, so it is kept unverified and drawn with red stripes.
  - Fronts come from the drawing: beds, chairs, sofas and counters all match the reference.
- **AI typing of drawn symbols** (§3): crops at a readable scale, two passes that must agree, a size-table veto,
  `not_furniture` kept but not built. The answers are committed as seeds (`results/recognition/<p>/`), so a re-run
  needs no vision model for them.
- **Scans and phone photos** (§4): rectify and deskew, OCR scale at 0° and 90°, wall mask, openings, rooms, room
  labels from two AI passes (or one pass equal to Tesseract). `synthetic-02` (scan + photo) is now `ok`
  (it was `needs_review`). With real AI answers (pod C0), real01 scan and real01 photo both get 8/8 room labels, and synthetic-02 gets 5/5.
- **DWG** (§5): LibreDWG 0.14 is built on the pod (GPL, run as a separate program) and feeds a generic DXF
  adapter. `synthetic-06` (a DWG drawn the way CAD offices draw) runs end to end.
- **Look** (decisions 6 and 8): `AgX - Punchy` is the default. A room with no furniture gets one view
  (none below 2.5 m²).
- **Library** (decision 7):
  - refit takes a library model only when its style tags include the project's style family or `neutral`,
    else the parametric mesh;
  - beds without a mattress are gone;
  - 50 new Objaverse models (CC BY 4.0, 16 types), each judged by both AI models on rendered thumbnails,
    with the front agreed. Credits are in every `ATTRIBUTION.md`, with the ODC-By notice (`results/library/`).
- **Added-object detector** (decision 3, §8.1): OWLv2 compares the Cycles and polished images. Calibrated on
  29 insertions and 260 harmless pairs: insertions confirmed 79 %, false confirmations 2.7 %. In the runs it
  rejected 3 polished views that the edge/depth gate had accepted (synthetic-04 living room: a fridge-like unit
  added in the far kitchen; synthetic-06 master bedroom; synthetic-03 balcony). The vision check stays advisory for absolute flags,
  as you decided.
- **Realism A/B v2** (decision 5, §8.2): one aspect per question, image order balanced inside the question and the
  answer. Result on synthetic-03 (Punchy vs look None, 32 pairs, 512 calls per model): **not measurable** by the
  rule fixed before the run. Qwen now passes all four known-direction controls (in M6 it missed the lighting one),
  but it fails the null re-encode control and picks the first image 74 % of the time; GLM misses two controls and
  always ties. Qwen alone prefers look None on lighting and photo (21 : 0), but the None renders are 0.3–0.5 EV
  brighter in nearly every pair, so that is not evidence. These judges cannot certify a look; a human rating can.
- **Orchestrator**: new stages (recognize, pipeline_final, detect), a `pending` state for projects waiting for
  AI answers, an 8-sequence tier for 96 GB GPUs, a prep job (`scripts/jobs/prep.sh`) for library, detector and
  recognition work. The RTX PRO 6000 measured 1.63× the PRO 4500.

Pod runs (RTX PRO 6000, $2.09/h; `docs/gpu-log.md`; M7 total **$10.43**):

| Pod | Content | Minutes | Cost | Result |
|---|---|---|---|---|
| prep 1 | recognition answers, Objaverse survey, detector calibration, GPU timing | 45 | $1.57 | exit 1: 5 problems found (fixed, see below) |
| prep 2 | the same after the fixes | 21 | $0.74 | ok except real01-photo labels 6/8 (P7, fixed later) |
| B | full run real01, synthetic-01, -04, -02, -06, -05 | 64 | $2.24 | 6 × ok; 4 GPU tests failed (found the camera problem below; the reversed bed was found in the images) |
| C1 | same six projects again after the fixes | 97 | $3.38 | 6 × ok; GPU tests 200 passed, 0 failed (22 not applicable) |
| C2 | synthetic-03 + realism A/B v2 | 55 | $1.93 | exit 1: synthetic-03 ok; 1 of 48 GPU tests failed (one view, open item); synthetic-05 A/B pairs missing (my setup: it was rendered in C1 without the alternate look) |
| C0 | raster fixtures (real01 scan and photo) with real AI answers; recognition, library and detector GPU tests | 16 | $0.57 | ok; GPU tests 16/16 |

Results per project (pod C1/C2; P = polished final, C = Cycles final):

| Project | Input | End state | Views | P / C | Gate validation | Detector rejects | Views with a final mismatch |
|---|---|---|---|---|---|---|---|
| real01 | CAD PDF (feet) | ok | 20 | 10 / 10 | flagged (0.946 / 0.90+) | 0 | 0 |
| synthetic-01 | DXF + vector PDF + scan | ok | 29 | 19 / 10 | ok | 0 | 1 |
| synthetic-02 | scan + photo | ok | 11 | 0 / 11 | polish disabled (negatives 0.83) | – | 1 |
| synthetic-03 | DXF, 3 levels | ok | 44 | 27 / 17 | ok | 1 | 0 |
| synthetic-04 | DXF + vector PDF | ok | 14 | 7 / 7 | ok | 1 | 1 |
| synthetic-05 | DXF + photo, polish off | ok | 23 | 0 / 23 | – (brief: no polish) | – | 1 |
| synthetic-06 | DWG | ok | 17 | 16 / 1 | ok | 1 | 0 |

Found and fixed on the way (each with a test):
- Prep 1:
  - the judge schema used `uniqueItems`, which vLLM rejects;
  - models of unknown units were dropped (now normalised by type, noted);
  - Objaverse category names did not match;
  - the AI typed weakly without the drawn facts (the question now gives the drawn size and the room);
  - a second question round ended in exit 4.
- Pod B:
  - **real01's south bed was built reversed.** Both AI models named one fixed side for every bed, and the old
    rule then dropped the drawn front. Drawn fronts now outrank AI fronts (CLAUDE.md trust order), and the
    disagreement is listed as a conflict.
  - **The camera search saw beds, chairs and toilets as full-height boxes**, and picked views of a bare wall
    "showing" a bed. Pieces with a back now have a height profile (low part + back), taken from the builder's
    parts.
  - real01-photo missed the bath and store doors (P7): a door frame nub and a door leaf fused to a wall in the
    photo's wall mask. Both are now recognised (scan and photo: 5/5 doors; 8/8 labels with real answers).
- Code review before the pods: 32 confirmed findings fixed, each with a test that failed first. One remainder is open:
  at a 30° rotation a nightstand's head line is taken by a window gap.

Needs your OK or action:
1. **real01 style**: no brief, so the defaults apply (Scandinavian, …), listed as assumed. Add
   `projects/real01/brief.yaml` with your style and the next pod re-runs style → refit → build → render → polish →
   check.
2. **Polish on real01** (decision 4): the gate passed with a flag. It also rejects some harmless edits (accepted
   94.6 %, target 95 %), so 10 views stay Cycles. Side-by-side sheets: `results/final/real01/contact_sbs_*.jpg`.
   Please look at them and decide again whether polish stays on.
3. **TRELLIS.2 was not built** (image-to-3D, decision 7). Generated shapes have no documented source. The
   parametric meshes cover the types the library lacks. Keep it out?
4. **Objaverse licences** are declared by the uploaders, not verified. They are fine for this PoC; check them
   before commercial use (flagged in `docs/plan.md` §4.8).
5. **Warm white walls with Punchy**: synthetic-01's white walls averaged R/B 1.104 with pod B's cameras (M5 limit
   1.10) and pass with C1's cameras. Bright wall areas are as neutral as in M6; shaded areas near the wooden floor
   pick up more warm bounce. Accept, or tone the look down?

Open items:
- Furniture from scans and photos: footprint recall 0.63 (synthetic-02 scan) and 0.30 / 0.20 (real01 scan /
  photo), targets 0.8 / 0.7. Touching pieces stay one cluster (unknown, unverified; nothing invented).
- The vision check (two VLMs) still rarely confirms removals and insertions (targets missed, advisory). The
  OWLv2 detector now covers insertions.
- Nightstand fronts come from the AI only (the drawing gives no unique front); 2 of 4 differ from the reference.
- synthetic-02's gate rejects only 83 % of geometry changes, so it keeps Cycles images.
- One GPU test is red on one view: synthetic-03 `cam_r_L0_mutfak_3`. The camera stands 0.45 m from an Objaverse
  vintage fridge with a rounded top. Its fitted box reaches the frame corner (2.7 % in the camera model), but the
  real rounded corner does not (0 % in the render). The box model cannot know a library mesh's shape. A fix
  would move cameras again and re-render every project, so I left it for the next look pass.
- The A/B for synthetic-05 did not run: its renders came from pod C1, which was not told to render the
  alternate look. It would not change the verdict, which fails on the judges' controls.

GPU cost so far: $19.17 of $100 (`docs/gpu-log.md`). No pod is running.

Next step: your answers to the five points above. Then Milestone 8 (to be planned with you).

## Decisions of 4 Oct 2026

| # | Item | Your decision | What it means |
|---|---|---|---|
| 1 | real01 style | you add `projects/real01/brief.yaml` later | then one pod re-runs real01 from the style on (≈ 25 min, ≈ $1) |
| 2 | AI polish | decide from the cost | see the table below |
| 3, 4 | Furniture | better furniture is a must; do whatever is needed; licences may be ignored for now | Milestone 8 (`docs/milestone8.md`): Amazon Berkeley Objects product models (CC BY 4.0), Objaverse of any licence (flagged), TRELLIS.2 generated models for the gaps, bed frames with real bedding, rugs and wall art |
| 5 | Warm white walls with Punchy | accepted | the GPU test limit becomes R/B ≤ 1.12 |
| 6 | Cameras | wider lenses | 18 mm (90° view), 16 mm in rooms narrower than 2.2 m |
| 7 | Daily GPU cap; faster machines | raised from $10 to $20, then to $30 per day; faster machines allowed | `CLAUDE.md` and `scripts/gpu_run.py` (`MAX_PER_DAY = 30`); the $5/h, 2 h per pod and one-pod rules stay. The RTX PRO 6000 stays first: the fastest GPU under $5/h for these runs (H100/H200 have no RT cores, so Cycles renders slower on them) |

AI polish cost (pods C1/C2, RTX PRO 6000 at $2.09/h; gate check + polish + added-object detector + half of the vision
check, which checks the polished images):

| Project | Views | Polish GPU time | Polish cost | Rest of the project | Polished finals |
|---|---|---|---|---|---|
| real01 | 20 | 10.8 min | $0.38 | $0.24 | 10 of 20 |
| synthetic-01 | 29 | 11.5 min | $0.40 | $0.40 | 19 of 29 |
| synthetic-03 | 44 | 23.9 min | $0.83 | $0.38 | 27 of 44 |
| synthetic-04 | 14 | 4.7 min | $0.16 | $0.25 | 7 of 14 |
| synthetic-06 | 17 | 4.0 min | $0.14 | $0.21 | 16 of 17 |

About $0.02 per view (≈ 25–30 s of GPU per view including its checks); every pod also has ≈ 20 min of fixed setup
(≈ $0.70) with or without polish.

## Milestone 8 – product-model furniture library, generated models, bed frames, rugs and wall art, wider lenses (done, 4 Oct 2026)

Spec: `docs/milestone8.md`. Five pods, $6.10 in all (`docs/gpu-log.md`: L1, L2, L3, L3b, F1).

- **Library** (`wenart/furniture/catalog_library.json`): 180 furniture models (124 Amazon Berkeley Objects, CC BY 4.0;
  38 Objaverse of any licence, flagged; 18 generated with TRELLIS.2 from Z-Image-Turbo pictures for the gaps:
  washing machines, kitchen sink units, showers, bathtubs, a fridge, a washbasin, plants) and 24 decor models
  (cushions, rugs, wall art). Every model was judged by two vision models; credits in `ATTRIBUTION.md`.
- **Builder**: bed frames get real bedding on their measured deck; rugs and wall art come from the library.
- **Cameras**: 18 mm lenses, 16 mm in rooms narrower than 2.2 m.
- **Full runs (pod F1)**, all `ok`:

| Project | Pieces from the library | Movable pieces from the library | Final images | Decor items |
|---|---|---|---|---|
| real01 | 17 of 22 | 16 of 17 | 20 Cycles (the gate turned the polish off) | 12 |
| synthetic-01 | 23 of 39 | 21 of 30 | 23 polished, 6 Cycles | 24 |
| synthetic-04 | 17 of 26 | 17 of 21 | 6 polished, 8 Cycles | 13 |

Open after F1: two real01 GPU tests failed. Both were test faults, fixed in Milestone 9: the detector test
counted old files from an M7 run, and the counter test measured a kitchen counter seen through a door from
another room.

## Milestone 9 – 20 models per type, more decor, AI decor in rooms with drawn furniture, 3D files (done, 4 Oct 2026)

Spec and details: `docs/milestone9.md` (§9 "As built"). Four pods, $7.77 (`docs/gpu-log.md`): L1, L2 and L3
built the library, F1 rendered real01 (you asked for real01 only). You stopped the library expansion after L3.

**Library** (`wenart/furniture/catalog_library.json`):

| | M8 | M9 |
|---|---|---|
| Furniture models | 180 | 453 (231 Amazon Berkeley Objects, 77 Objaverse, 145 generated with TRELLIS.2) |
| Decor models | 24 | 152 (114 ABO, 38 generated) |
| Furniture types with 20 models | 0 of 24 | 16 of 24 (18 of 24 with the 30 Poly Haven base models the fit also uses) |
| Decor types | 3 | 8: cushion, rug, wall art, and new: table lamp, vase, mirror, bowl, small plant |

Below 20 models: shower 10, kitchen sink 15, toilet 17, fridge 18, stove 19, washbasin 19 (the two judge models
refuse many generated sanitary and kitchen models), bowl 18, wall art and mirror 17.

**AI decor**: a vision-language model (Qwen3-VL-8B, two passes at temperature 0, strict schema) decorates every
furnished room, including the rooms whose furniture comes from the plans. It only picks from checked places (tops,
sofa and bed cushions, shelves, walls, free corners, rug areas) and never moves, adds or removes furniture; an item
is built only when both passes agree. real01: 19 items in all 5 rooms with drawn furniture, no rule fallback.

**3D files**: every full run now also writes `<project>.blend` (opens in Blender: packed textures, the render
cameras with their exposure) and `<project>.glb` (glTF for other 3D tools). real01: 75 MB and 151 MB, sent to you
as six 24 MB zip parts (the app refused the single big files); `python -m wenart.run.pack3d` makes the parts.

**real01 (pod F1)**: ok, no GPU test failed (48 run, 10 skipped). 20 Cycles images: the gate validation turned the AI polish off
again (it rejects only 87.7 % of geometry changes, needs 90 %), as in M8.

Open items (none blocks M9):
- real01 polish stays off until the gate rejects ≥ 90 % of geometry changes on it.
- The vision check misses most removal and insertion controls on real01 (advisory only).
- One drawn piece of real01 (f_L0_018) stays untyped: the two AI passes disagree or do not answer (unverified,
  footprint kept).
- The other projects get the new library, AI decor and 3D files on their next full run.

GPU cost so far: $33.04 of $100. No pod is running.

## Milestone 10 – whole building from the sheets, AI completion of furnished rooms, a larger library (done, 9 Oct 2026)

Spec and details: `docs/milestone10.md` (§10 "As built": tracks, decisions, code review, pods, GPU test failures,
acceptance). Ten tracks built it in parallel; a review workflow (58 agents) found 47 confirmed issues, all fixed.

**Feature 2, the whole building.** A new `sheets` stage splits a CAD sheet into its drawings (plans, alternative
plans, sections, title blocks), reads titles, levels, variants and units, registers the plans and takes the heights
from the section. The build stacks the levels on slabs, connects the stairs, puts the attic under its roof (gable or
mansard from the section), adds the facade and the site, and renders 5 or more exterior views (an alternative
with the same outside shows the base's). A design alternative (real02's basement "Açık mutfak") runs as its own sub-output with only its changed rooms.

**Feature 1, AI completion.** In rooms with drawn furniture the AI adds the pieces the room type misses (both
passes must agree; the placer checks every piece); drawn pieces keep their place and front.

**Feature 3, the library and the looks.** 53 named colours, 25 wall finishes, 32 floors, kitchen fronts, worktops
and handles, 8 door styles, 6 window frames, 28 exterior materials, 9 lighting moods; real02's brief is fully
matched.

| Library | M9 | M10 |
|---|---|---|
| Furniture models | 453 (24 types) | 669 (37 library types + `wall_cabinet` built parametrically) |
| Decor models | 152 (8 types) | 363 (20 types) |
| Models with material slots and tags (both judges) | – | 931 of 1032 (recolourable: fabric 117, wood 157) |

**Acceptance projects** (pods F1b, F2, F3):

| Project | End state | Views | GPU tests |
|---|---|---|---|
| real02 (acceptance) | ok (was `needs review`) | base 42 + 5 exterior; alternative 12 + 5 exterior | green |
| real01 | ok (the gate now allows the AI polish) | 20 | green |
| synthetic-03 | ok | 44 | 1 failure: a camera-model bug, fixed in code, not re-run |
| synthetic-07 | ok | 30 + 3 (alternative) | green |

**GPU**: 13 pods, $31.88 (`docs/gpu-log.md`). The first library pods lost time to a slow copy on the network
volume and to the watchdog (fixed: faster copy, the job ends before the watchdog, retries fetch only missing
files). With your OK the network volume grew from 120 to 250 GB (about $17.50/month) after it filled up.

The full runs found 7 code defects that the CPU tests could not see, and 5 GPU tests that needed Milestone 10
updates; all are fixed with tests (§10.6–10.8). The visible defects: a lost attic gable wall, a roof ridge line read
as furniture, a camera in a stair well, and attic stairs built as new flights through the roof.

Open items:
- real02 and synthetic-03 were not re-run after the last two fixes (you asked to stop after F3): the committed
  real02 exterior views still show the two attic stair shafts above the ridge. One pod (`RUN_PROJECTS="real02
  synthetic-03"`, about 90 min, about $4) would show the fixed versions.
- real02: 20 of 38 rooms are unverified: 18 because their area labels differ from the measured areas by more than
  3 % (corridors with their stair halls, an open kitchen labelled 8.5 m² in a 52 m² space), 2 because they are
  unlabelled stair cores; 58 drawn pieces have no agreed type. They render with red stripes. Relaxing the area rule
  would be your decision.
- The exterior views stay Cycles renders: the exterior gate rejects only 84.6 % (real02) and 71.7 % (synthetic-07)
  of geometry changes (needs 90 %).
- Below 20 models: crib 8, display cabinet 8, bunk bed 10, chaise 10, shower 10, kitchen sink 15, tall cabinet
  17, and 7 types at 18–19; decor below the target of 15: blind 9, large plant 10 (5 more decor types have 17, bowl
  19; §4.11 has the reasons). 101 generated models have no material fields.
- An AI-added parametric toilet is built 1.2 m tall (two meanings of a toilet's height; fixing it changes real01).
- Other known limitations: `docs/milestone10.md` §10.4.

GPU cost so far: $65.68 of $100. No pod is running.


## Milestone 11 – AI orchestrator (steps 0–1 done, 9 Oct 2026; waiting for your OK)

Spec: `docs/milestone11.md` (the user named `docs/milestone10.md`, which is the M10 spec).

- **Step 0, diagnosis of real02** (§1): 41 problems traced to their stage and code, in three tables (exterior 14,
  furniture 17, rooms/materials/cameras 10). The main causes: 107 of 226 drawn pieces had no front, so they faced a
  fixed direction; whole kitchen runs and table-with-chairs blocks read as one box; the "unverified" stripes are
  painted into the final images; the default "light tiles" were a black/beige marble checkerboard; the grass plane
  ended 30 m from the house; text labels ("Teras") cut a roof the section draws closed.
- **Plain bugs fixed now** (each with a CPU test that fails on the old code): ground to the horizon, attic decor
  kept under the roof, terrace paving, sky and sun in one frame, light ceramic wet tiles, debug-image window and
  stale previews, block pieces take the drawn front (washbasins, toilets, beds, wardrobes), AI fronts into a wall
  refused, pillow-rule ties, shallow pieces' wall rule, added chairs face their table, unknown boxes that hold other
  pieces drawn flat. They show in the images after the next pod re-runs the projects.
- **Step 1, design** (§2–§14): agent loop over the existing stages, typed tool API, edit validator, overrides file,
  critic checklists, feedback routing, decision log, layout-engine and exterior work, test plan. Model pick:
  `Qwen/Qwen3.8-27B-FP8` (Apache-2.0) as agent and vision critic on the RTX PRO 6000 next to Cycles; fallback
  `Qwen/Qwen3.6-35B-A3B-FP8`. Three pods, ≈ $12.
- **Your OK of 9 Oct 2026** (D1–D8): `CLAUDE.md` updated (`d602269`); D5 and D6 became brief options with
  evidence-based defaults (§17), still open questions about real02. Contracts frozen (§17, `fa31d58`); the build
  runs in three parallel tracks: A agent core, B layout engine, C exterior/rooms/cameras.

GPU cost so far: $65.68 of $100 (no pod in M11 yet). No pod is running.

### Milestone 11 – build and pods (done, 10 Oct 2026)

Spec and report: `docs/milestone11.md` (§18 as built, §19 pods, §20 report).

- Built: the agent (`wenart/agent/`: model client, 30 typed tools, overrides, code + vision critics, per-room
  planner, rounds, router, decision log), the layout engine (plausibility F1–F9/R1–R4, orientation rules, groups,
  wall snapping, validated edit ops, type inference, splitting at ingest), the exterior (roof from the break line,
  site with paths, hedges, trees and sunken courts, facade bands, physical sky, new cameras), kitchens with
  splashbacks, no stripes in final images. Orchestrated is the default; `--no-orchestrator` keeps the M10 chain.
- Agent model: `Qwen/Qwen3.8-27B-FP8` (Apache-2.0), 46 tokens/s, 52 GB next to Cycles on the RTX PRO 6000.
- Pods: G1, G2, G2b, G3, G2c, G2d: 382 min, $15.85. The real02 runs found and fixed 10 integration problems
  (planner, lock check, rollback, time budget, camera and light, GPU tests).
- Results: real02 (G2d): 4 rounds, 20 edits accepted, complete; real01 (G3): 4 rounds, 5 edits (living room fixed:
  score 80 → 100); synthetic-01: 1 edit. Before/after sheets: `results/compare/<p>/before_after_*.jpg`.
- GPU tests: G2d 37 of 39 (1 fixed in the test, 1 open: §20.4 #3).
- CPU tests: the final full run gave 4292 passed, 8 failed; all 8 were tests reading the committed real02 results
  (now the M11 ones), the G1 folder name and the terrace depth limit; fixed (F1b data frozen in
  `tests/fixtures/m11_f1b/`), those files pass (70 tests).
- Open items: §20.4 (grey boxes in real02, many major findings still open, polish off in orchestrated runs).

GPU cost so far: $81.53 of $100. No pod is running.

### real03 ingest: walls inferred from labelled room outlines (10 Oct 2026)

`projects/real03/` (the user's D Blok ground floor, public like real02): the flats are external references that are
empty in the DWG, so only the shared core is drawn: its walls layer holds four jamb fragments, but every core room is
a closed net-area outline with its label and printed area.

- Sheet frame blocks (`wenart/ingest/generic/frame.py`): a frame and title block inserted as one block (real03's
  legend `*U62`) are no plan geometry; before, two title-block rows were the only "walls".
- Walls from room outlines (`wenart/ingest/generic/outlines.py`, CLAUDE.md "open outer walls -> infer first"): when
  the drawn walls do not close, closed outlines holding exactly one label (area within 8 % of the printed one) give
  the walls: inner walls fill the gaps between outlines (≤ 0.60 m), outer walls 0.25 m (or the drawn fragments'
  median); drawn walls on them stay `vector`; every inferred wall has evidence method `inferred`, `inferred: true`,
  status `unverified`, a warning and a report table. Doors and windows are read only where their symbols are drawn;
  rooms without a door get a warning (none invented).
- real03: status ok (was needs_review), 30 inferred walls, 5 rooms with the printed areas, 4 door leaves (two glass
  double doors), 3 unknown pieces for the AI, 3 rooms without a drawn door. Tests: `tests/test_outline_walls.py`.

### real03: the whole ground floor (10 Oct 2026)

The user saw only the core. The flats were in `tekkat.dwg` all along; details in `docs/milestone11.md` §19.8.

- LibreDWG `dwg2dxf` dropped 13 blocks (a loop-index bug): one-line patch in both setups (`0.14 d9468ae p1`).
- XCLIP boundaries of block references honoured; walls drawn as closed outlines per room (`ring`); concrete core
  walls (`MYD - BA`, `B-H`); 15 mm slit closing; inner wall stubs and open balconies no review reasons;
  services-layer texts no room labels; room types `stair` and `shaft` (never furnished); `YAŞAMA` living.
- Agent: may retype or remove fixed equipment in a room that never holds it; new `set_lighting` tool; edits tied
  to the building they were made on. Lights: one per 3 m in long rooms; only windows in outer walls bring daylight.
- Pods: 3 runs ($6.10). Run 3: 8 flats + core, 84 views, every room lit, agent 2 rounds; GPU tests 37/39.
- Open: white boxes in some living rooms (untyped drawn pieces), 2 GPU tests, no exterior view.

## Milestone 12 – ground levels, furniture overhaul, smarter pod AI, library audit (built 11 Oct 2026; GPU re-check of the last fixes open)

Spec: `docs/milestone12.md` (prompt: `docs/prompts/milestone12.md`). Cloud session, CPU only, no pod, no code change.

**Step 0, diagnosis** (§1, five read-only reviews, every count by script):
- **Furniture** (§1.2): most drawn pieces are not read into usable pieces (real03: 42 built `unknown` boxes, 6 unbuilt
  clusters over 92–100 % of their rooms, no kitchen counter, sink, fridge, washbasin or dining set built; room-number
  circles and a level mark built as furniture). The AI adds single pieces with raw coordinates; the placer repairs each
  alone; the 5 group templates are used by no stage; the checks count partners, they never judge the arrangement.
- **Decor** (§1.3): cushion and throw heights come from a type table (bed 0.55 m, sofa seat 0.45 m), not the built
  model; agent edits leave the decor behind; throws in the library include a juice machine and benches squashed to 5 cm.
- **Agent** (§1.4): real03 run 3: 5 accepted, 73 rejected (53 aimed at pieces no tool may change: locked fixed equipment
  with misread sizes, unbuilt pieces); 12 of 35 rooms reached (120 calls per round, final-stage estimate 15 min too
  long); no plan, memory or dry run.
- **Levels** (§1.5): no level mark on plans, site plans or in blocks is read (the pattern rejects `+-0.00`, `KOT:`,
  `SB. KOTU :`); no room floor levels, door thresholds or terrain; the ground floor always sits at grade; single-region
  projects (real01, real03) get no site and no exterior view.
- **Library** (§1.6): 1032 models (ABO 538, Objaverse 213, generated 281); 68 of 333 (type, style) pairs empty
  (mediterranean 21); both judges accepted wrong objects (an air bed, "Corpse" as a throw, street lamps); 114 models
  with wrong heights; the judges' quality score is never used (bug B1).
- 11 plain bugs listed, not fixed (§1.7).

GPU cost so far: $89.37 of $200. No pod is running.

**Your answers of 10 Oct 2026:** misread fixed equipment may get a real product size and move ≤ 0.5 m (logged);
real03 exterior with the ground floor only; the 18 NC/SA Objaverse models are removed from the catalogue.

**Step 1, design** (`docs/milestone12.md` §2–§12, decisions D1–D24, sources checked 10 Oct 2026):
- **Levels** (D1–D6): one reader for every level mark (texts in the Turkish forms, block attributes, symbols) on
  plans, sections and site plans; new fields (marks, room floor offsets, door thresholds, ground points, terrain,
  entrances, plinth); steps/ramps/plinth/terrain inferred and built; single drawn floors get a site; checks L1–L7;
  level tools for the agent. Default when nothing is drawn: the ground floor 0.15 m above the ground (D3a).
- **Furniture** (D7–D15): read every drawn piece first (symbols are never furniture; untyped pieces are not built but
  listed); groups as data; a program per room; a deterministic group solver returning 3 candidates, the VLM only
  chooses; group checks G1–G14 (NKBA / UK Part M minimums as hard checks) and scene checks S1–S6; decor in its host's
  frame, ray casts and shrinkwrap on the built mesh (gap ≤ 1 cm, penetration ≤ 1 cm hard / 3 cm soft); audited models
  only. Reuse: Holodeck's constraint vocabulary (Apache-2.0), Infinigen's hard/soft split (BSD-3), ProcTHOR's group
  format (Apache-2.0); no learned model (3D-FRONT is non-commercial).
- **Agent** (D16–D20): a model bake-off on our own tasks (Qwen3.8-27B FP8/BF16, Muse-Glimmer-30B, and on 2 GPUs
  Qwen3.8-Flash-Next with a flagged custom licence); a room brief with locks and allowed edits, group tools, dry run,
  a plan per room, memory across rounds, parallel sessions, a measured time budget, metrics.
- **Library** (D21–D24): an audit job (scale-referenced thumbnails, code and vision checks, keep / fix / remove, a
  contact sheet per type), nothing deleted without your OK, one size table, a gap report; growth from Poly Haven CC0,
  procedural textiles and fixtures, Infinigen fixtures, an ABO style pass, GSO decor, each after your OK of its list.
- **GPU estimate:** ≈ $35–49 (1 GPU) or ≈ $55–80 (agent on 2 GPUs) → ≈ $124–169 of $200 in total.

GPU cost so far: $89.37 of $200. No pod is running.

**Your OK of 10 Oct 2026:** D1–D24, D3a (0.15 m), D16 (bake-off with Qwen3.8-Flash-Next on 2 GPUs; 2-GPU full runs if
it wins by ≥ 10 points), the GPU plan with `--over-5-ok` for P1 and 2-GPU pods, `CLAUDE.md` wording 1–5 (applied,
`842bbef`).

**Step 2, build (started 10 Oct 2026):** contracts frozen (`docs/milestone12.md` §13, `4a6701e`: stubs with fixed
signatures, pipeline and build hooks, schema fields, DXF attribute tags in the text evidence, `scripts/gpu_run.py
--gpu-count 2`); six tracks build in parallel: L levels, R reading, G groups and solver, S scene/decor/fit,
A agent/run/bake-off, B library audit.

**Step 2, build and pods (11 Oct 2026)** (`docs/milestone12.md` §14):

| Pod | What | Result | Cost |
|---|---|---|---|
| P1 | agent model bake-off (4 models, 8 variants) | **Qwen3.8-27B-FP8, thinking off** stays: 40.6 points; Flash-Next 46.2 but 2 GPUs (rule: ≥ 10 points better); no model judges layouts from images (T3 at chance), so layout errors stay with code checks | $17.31 (of which failed tries $9.81) |
| P2 + P3 | library audit (1,066 models) | after 6 rule fixes and your decision 1a: keep 907, fix 29, removed 126, 121 kept with a vision doubt | $2.51 |
| P4 | library growth (your 4 lists) | 352 catalogued, 314 usable (Poly Haven 70, ABO 196, GSO 31, Infinigen 17); 1,250 usable models now; gaps 269 → 227 | $1.43 |
| P5 | real03 full run | 85 / 179 agent edits accepted; GPU tests 29/39 → 2 scene fixes, test updates, 5 agent fixes | $4.08 |
| P6 | real02 full run (basement, attic, variant) | 119 / 172 accepted; GPU tests 38/39 (a 1–2 px gap by a door leaf) | $3.91 |
| P7 | real01 + synthetic-01 | real01 23 / 18 accepted; GPU tests 72/75 → 2 fixes, 1 open | $3.12 |
| P8 | real03 rerun | **65 / 35 accepted** (65 %, P5 32 %); GPU tests 37/39 → both fixed on CPU | $3.99 |

What changed for the user's five problems (real03 P5 → P8 unless noted):
- **Levels:** level marks read (real03 datum 93.20, real02 43.00); ground 0.15 m below the ground floor where
  nothing is drawn; single-floor projects get a slab, roof, site and exterior views (real03: 6).
- **Furniture:** drawn pieces read first, symbols never built, untyped pieces not built but listed; groups placed by
  the solver; 159 of 171 drawn pieces stay as drawn (P5 154).
- **Decor:** rests on the built mesh of its host; a cushion with nothing to lean on is not built.
- **Agent:** accepted share 32 % → 65 %; the brief offers only edits that can pass (relayout and completion dry runs,
  no moves of drawn groups, group-keyed retry limits); agent cameras checked for free floor.
- **Library:** audited (keep / fix / remove with evidence, contact sheets per type), grown by 314 usable models.

Fixes after P8 (CPU, tests green, full CPU suite 4,851 passed before them, the 2 failures fixed): only windows and
doors cut through overlapping walls (a slit to the outside), agent cameras on free floor (a camera 5 cm from shower
glass), 108 → 41 wall cuts on real03, complete_group only after a passing dry run, build phase timings, a program
crash on a double bed in a room under 9 m².

Open (`docs/milestone12.md` §14.7): GPU re-check of the after-P8 fixes (next pod, ≈ $4); real03's scene build was
twice as slow in P8 (cause not found on CPU; the new phase timings will show it); a door-leaf gap (cosmetic); an AI
kitchen sink inside its counter run (synthetic-01); bathroom cameras that do not see a door leaf; window pull 89 %;
48 kept models whose vision check names another type (a retype rule is your call); place_group 0/4.

GPU cost of Milestone 12: $36.35 (estimate $35–49). Project total: **$125.72 of $200**. Today (11 Oct UTC):
$27.09 of $30. No pod is running.

### After Milestone 12: more pod time, several buildings on one plot, real04 (11 Oct 2026)

**Your requests of 11 Oct 2026:** pods get more time; run the attached DWG as real04; several buildings can stand
on one plot ("r14 is gorgeous the ground slope"); the USD limits may be passed for this test.

- **Pod time:** 4 h per run (was 2 h; `CLAUDE.md`, `scripts/gpu_run.py`), `AGENT_ROUNDS` for the full job (real04:
  6); 11 Oct only: day cap $60, `--over-5-ok`.
- **real04** (`projects/real04/deneme1.dwg`): the real02 twin villa with its site. The site plan r14 holds two
  twin-villa blocks (4 villas), the plot (1,165.9 m²), four 24 m² pools with sun terraces, parking, 101 trees and 16
  level marks (37-46 m).
- **Several buildings on one plot** (`wenart/sheets/buildings.py`, `wenart/blender/copies.py`): every copy of the
  building on the site plan is found (b2 18.6 m beside b1, **3.00 m higher**), turned the right way by its entrance
  markers, raised by the marks at its entrances (±0.00 = 43.00); the ground is a sloped surface from the site
  marks; the pools are built; b2 is an instance of b1 in the scene; the exterior views keep clear of it and one
  site view shows both blocks. Tests: `tests/test_site_buildings.py`, `tests/test_sheets_real04.py`.
- **real04 pod** `jeqodk9uyn9o6p` (114 min, $4.72): 6 agent rounds (182 / 170), 48 views rendered (44 interior, 4
  exterior incl. the site view of both blocks), b2 placed as planned. The rebuild for the final check's one edit
  failed: **the network volume is full** (disk quota); the GPU tests did not run. Fixed after: the site view's
  black area (a sloped ground now reaches the horizon). Open: the volume (your OK), the library gaps of the corner
  sofa and the long dining table.

GPU cost: $130.44 of $200 in total; 11 Oct: $31.81 of $60. No pod is running.


## Milestone 13 – realistic furniture, real vegetation, designer placement (done, 23 Oct 2026)

Spec: `docs/milestone13.md` (prompt: `docs/prompts/milestone13_fable.md`). Cloud session, branch `Claude/Fable_01`,
CPU only, no pod, no change to pipeline code. A 60-agent workflow did the work (3 image reviewers over all 182
committed renders, 6 diagnosis agents, 6 research agents, 45 licence/count verifiers, 3 proposal writers, 3 critics).

**Step 0, diagnosis** (§1): every committed render tagged and scored (`results/review/m13_step0/`): real04 (M12 code)
mean 1.88 of 5, real02 1.78, real03 1.85 (M11 code; the committed real02/real03 results predate the M12 solver and
audit). Ranked causes with numbers: (1) drawn anchors left empty by the fit (real04: 43 pieces not built, 20 of 33
drawn anchors, 4 of 8 bedrooms without a bed, 4 of 4 living rooms without a sofa; the library has no model near the
drawn sizes and M12 D14 forbids a built fallback); (2) weak model choice (a "recolourable wood first" re-sort
overrides the ranking: one Objaverse chair of unknown units used 40-42 times; audit quality, units, faces never
rank; half the pieces stretched > 5 %); (3) daylight 300× too weak (sun 3 W/m² vs 1000 reference; daylight rooms at
+3..+8 EV, panes pulled dark); (4) flat shell materials on 72-81 % of every frame, no displacement/sheen/coat/bevel/AO,
the brief's fabric colour never applied; (5) placement blocked by invisible drawn obstacles (unbuilt anchors, 44
untyped pieces); drawn groups not units; 84 % of round-1 findings survive 6 agent rounds, 20 of 160 accepted edits
removed their finding, the agent is 56 % of the pod; (6) outdoor: 101 hedge circles read as 4 m lollipop trees, flat
ground, pool boxes 1-2 m out of the ground, no sun disc, black below the horizon, 3 of 7 exterior cameras dropped;
(7) 18/16 mm lenses at 1.25 m and 12 of 48 views on bare landing walls. 13 plain bugs listed (§1.8).

**Step 1, research and design** (§2-§4): sources checked against official pages (HSSD, 3D-FUTURE/FRONT, ABO, Poly
Haven, ambientCG, TexVerse, Objaverse++, OmniObject3D, BlenderKit, Sketchfab, Fab/Megascans, Infinigen, Sapling,
TRELLIS.2, Pixal3D, Hunyuan3D, SAM 3D, PartCrafter, Material Anything, Holodeck, LayoutVLM, SceneEval, 2026 layout
papers, NKBA, Turkish minimums, Blender 5.2 levers); 45 verifiers refuted or corrected the decisive claims (§2.6).
Key facts: no commercial-safe source has real bath/kitchen fixtures (HSSD, CC BY-NC 4.0, is the only one); no
permissive professional layout data exists; open VLMs judge layouts at chance (code decides); Sapling runs headless in
bpy 5.2.2; every existing generated model was exported with the NC tool nvdiffrast; the real pod price is $2.49/h,
not $2.09. Three complete approaches (A quality-first relaxed, B commercial-safe maximum, C procedural/generative
first) with critics' verdicts and a comparison table (§3-§4).

**Recommendation** (§5-§9): build the licence-neutral core first (anchor never empty with module builders, fit
ranking, placement units, agent acceptance by "finding gone", physical daylight and light rigs, shell PBR with
displacement/sheen/coat/bevel/AO, 24 mm cameras, hedge detector + real/generated trees + site platforms + pools +
sky), grow the library commercial-safe (ABO by size grid, Poly Haven 2K with its 20 CC0 trees, ambientCG), add HSSD
as a switchable relaxed layer if its terms are accepted; licence switch with per-render `commercial-safe` line and
ATTRIBUTION sections; 17 before/after metrics on frozen cameras; 6 pods ≈ $46-54 at $2.49/h (project total needs a
raise to $230); 7 `CLAUDE.md` wording changes; 10 decisions (§10).

GPU cost of this step: $0.00. Project total: **$130.54 of $200**. No pod is running.

### Milestone 13, step 2 (build and pods, 15-23 Oct 2026)

- **Decisions of 12 Oct 2026** (D1-D10, `docs/milestone13.md` §12): relaxed licence mode for the PoC projects, HSSD
  layer (terms accepted by the user), flagged generated models kept (`tool_nc`), fallback ladder with good-looking
  fallbacks, drawn groups as units, project total $300, cameras and polish unchanged, no paid packs. Later the same
  day: no Milestone 12 baseline pods; the committed M11 runs of real02/real03 (commit 93aff07) and the committed M12
  run of real04 (eddde01) are the baseline. Pod B0a was stopped after 4 min ($0.19).
- **Contracts** (§13, commit c2a6a9e): eight tracks on disjoint files, frozen interfaces, new schema fields
  (`asset.method | ladder | licence_flag | commercial_safe`, `size_snap`, `drawn_group`, `site.hedges`,
  `site.platforms`, `project.licence_mode`), `library.licence_mode` setting.
- **Build round 1** (commit e1532a8, 15 Oct; the 12 Oct attempt was cut by a usage limit): 141 files (108 modified, 33
  new; +78,945 / -2,684 lines, of which 52,351 are the committed growth lists and 14,471 code); tracks T1-T8 built, reviewed and integrated by 17 agents; CPU suite 4,866 passed, 211
  skipped, 1 failed (`tests/test_models_assets.py::test_catalog_ids_exist_on_the_api`: the live Poly Haven API now
  reports `vintage_wooden_drawer_01` at twice the committed size; the entry is unchanged and is re-measured on the
  next library pod). Numbers per track go to `docs/milestone13.md` §14 after round 2.
- **Build round 2** (running): the cross-track wiring the integration left for the lead (HSSD as a catalogue
  source, code typing before the recognition questions, rug members and solver candidates in the edit ops, agent
  routing by cause, site object kinds, camera-replay flags, agent rounds 3, the contracts test, manifest records for
  the metrics) and the §14 draft.
- **Pods**: P1 (pod `ker0qemve1rhpf`, RTX 4090 at $0.89/h, worst case $3.56, 4 h) runs the lever A/B (light), the
  site A/B (vegetation, platforms, pools, sky) and the GPU tests of T2/T5/T6 on the round-1 code (33d12db). The
  runner now leaves a running pod to its own watchdog when this session kills it after 2 h (`attach` collects later).
  Next: P2 (library downloads and audit, HSSD included), then P3/P4/P5.
- GPU spent so far: $130.73 of $300 (+ P1 when it ends). One pod running (P1).
- **Pod P1 done** (15 Oct, RTX 4090, 163 min, $2.42): lever and site A/B rendered (`results/review/m13_p1/`), decisions in
  `docs/milestone13.md` §14.3 (sun 1000 W/m², rig on at gain 2 with daylight-only white balance, EV cap, shell; Poly
  Haven tree instances, hedges, platforms, pools, sky with a camera-only sun disc). Two GPU tests to fix (round 3).
- **Pod P2 done** (15 Oct, RTX PRO 6000, 46 min, $1.90): 884 new models catalogued and audited (ABO by size grid,
  Poly Haven at 2K with vegetation, ambientCG sets); the catalogues in the repo now hold 1,950 entries (usable
  commercial 1,519, relaxed 1,777); coverage 57 / 64 of 90 demand bins. **HSSD: 0 of 874, HTTP 403: the account
  behind the pod's `hf_token` has not accepted the dataset terms** (§14.6); re-run after the acceptance.
- GPU spent so far: $135.05 of $300. No pod running.
- **16 Oct 2026**: the user accepted the HSSD terms (account behind `hf_token`). Round 3 of the build resumed after the usage
  limit (placement continues from its partial edits; a library agent adds the HSSD-only job mode). Next: round 3 green →
  commit → pod P2b (HSSD layer, ~30 min) → pod P3 (real04 full run).
- **Round 3 committed** (47bd941; CPU suite 4,988 passed, 0 failed). **Pod P2b** (16 Oct, $3.35): all 874 HSSD objects
  downloaded, 852 catalogued, 229 audited usable (furniture first); 560 still pending (the fixtures among them) → pod P2c
  finishes the audit, then pod P3 (real04 full run). GPU spent: $138.40 of $300.
- **Pod P2c** (16 Oct, RTX PRO 6000 WK, 52 min, $2.25): the HSSD audit finished (answers of P2b reused): 852 HSSD
  entries, 736 keep, 32 fix, 84 removed → 768 usable. The catalogues hold 2,681 entries (library 1,955, decor 726);
  usable commercial 1,417, relaxed 2,443. Relaxed dry fit: fixtures from the library real04 34 / 48, real02 32 / 38,
  real03 31 / 39 (§14.6). Fit fixes for the grown catalogue (no model search for pieces that are not built; dining
  tables and desks keep their working height within ±8 %) in 60611a6.
- **Pod P3, attempt 1** (16 Oct, RTX PRO 6000 WK, 27 min, $1.15): exit 1 at the layout stage; the locked check
  compared the two snapped YATAK beds with their re-solved size (fix: the drawing stays the reference, `locked.drawn_value`).
  Then a **CPU pre-flight** of every later stage on P3's real inputs found and fixed 11 more bugs (3ed3383, §14.8),
  among them the EV floor that clamped every sunlit view near white.
- **Round 4** (fe86436 and a follow-up, 16 Oct): calibrated exterior sky (7.71 at 35°, sky band now blue), chair v2,
  shell texture sets fetched and in the build fingerprint, `lighting_dark` read by the agent (a too-weak
  `set_lighting` keeps the finding) and the report, drawn fixed equipment protected from `mark_not_furniture`, a
  recognition whitespace guard (§14.8).
- **Two adversarial reviews of the follow-up** (16 Oct, 31 agents; commits 1a753e1 and 3724033): 7 real defects
  fixed with tests, among them a lighting rule that never fired on the real finding shape and a dry re-check that
  brought back findings an earlier edit of the round had removed (they could reject unrelated edits). A view that
  needs more than set_lighting's x3 is now report-only (an edit counts only when its finding is gone). Pod P3 attempt
  2 is pinned to 3724033 and waits for an 80 GB GPU in EU-RO-1. GPU spent: $141.80 of $300.
- **Pod P3 attempt 2** (16 Oct, RTX PRO 6000, 114 min, $4.73): real04 ran end to end (3 agent rounds, build, render,
  report). 34 of 34 drawn anchors built (M12: 12), no grey boxes, 91 HSSD pieces, real vegetation, agent edits that
  really removed their finding 74 % (M12: 18 %). Light and colour are worse than M12 (orange cast in 24 of 48 views,
  a night-dark bedroom, black terrace skies, blank windows); 4 GPU tests failed (2 stale pins, 2 real defects).
  Sheets and metrics: `results/review/m13_p3/`. Next: a fix round on CPU, then P4 (real02 + real03) and P5
  (real04 again with the GPU tests). GPU spent: $146.53 of $300. No pod running.
- **Fix round after P3** (16-17 Oct, CPU only, no pod; `docs/milestone13.md` §14.9). Part 1 (62b2b3c): light and
  colour (mixed white point, terraces under the exterior sky, sky and deeper window pulls, the fill light back in
  windowless bedrooms), door stops, drawn sinks built into their run and stove gaps, no extra wall from a secondary
  plan page, the agent's context budget, audit title flags, corrected metrics. Part 2: a review of part 1 found 22
  defects (3 major: the built-in sink's own unit filled its bowl, the results copy still shipped stale previews, the
  inner-wall camera rule had no test that could fail); all fixed, each with a test that fails on 62b2b3c or on a
  mutation of the code it covers. The planner's answer
  budget is now min(4096, room left); terraces render with the exterior clip; the lawn relief keeps paths, steps and
  plants on the ground; P4 re-pitches the replayed aerial ext_5 so it shows the sky.
  Track I_ingest: tests now cover the inner-wall camera obstacle (points and fallback), the crop collision through
  `run_project`, the 25 % missed-piece rule, the one-extra-per-missed-piece rule and the door span rule in the
  two-page run, and the never-asked `open_questions` and withdraw paths. Each test was checked with a mutation of the
  code it covers. `full.sh` gains `RUN_FRESH_RECOGNITION` for P5. Module code (`pipeline.py`, `reading.py`,
  `camsearch.py`) is unchanged.
  Full CPU suite after the part-2 integration: 5191 passed, 214 skipped, 4 xfailed, 0 failed (59 min). GPU spent
  in the fix round: $0.00. Next: P4 (real02 + real03) and P5 (real04 with `--env RUN_FRESH_RECOGNITION=real04`).

### Milestone 13 – done (23 Oct 2026)

After the fix round after P3: pods P4a (real02, $4.29), P4b (real03, $5.75), P5 (real04, $5.98), P6a (real04, $7.34),
P6b (real03, $6.24 + $0.27 fetch) and P6c (real02, $5.38), each followed by a CPU fix round with tests and reviews
(`docs/milestone13.md` §14.10-14.17). By your decision of 23 Oct 2026, P6a, P6b and P6c are the final results.

| | real02: M11 → P6c | real03: M11 → P6b | real04: M12 → P6a |
|---|---|---|---|
| Views better / same / worse | 32 / 6 / 3 | 41 / 10 / 8 (interior) | 31 / 11 / 5 |
| GPU tests passed / failed | 47 / 0 | 42 / 6 | 45 / 2 |
| Drawn anchors built | 29/30 → 40/40 | 15/15 → 27/27 | 12/34 → 36/36 |
| Agent edits whose finding is gone | 24 % → 73 % | 69 % → 88 % | 13 % → 91 % |
| Library share of built pieces | 58 % → 80 % | 56 % → 77 % | 67 % → 81 % |
| Interior views at EV ≥ +5 | 9/35 → 0/35 | 27/83 → 0/83 | 9/44 → 0/43 |
| Results | [`results/review/m13_p6c/`](../results/review/m13_p6c/) | [`results/review/m13_p6b/`](../results/review/m13_p6b/) | [`results/review/m13_p6a/`](../results/review/m13_p6a/) |

- **Your decisions of 23 Oct 2026**: the windows-only interior sky (+3.5 stops) is the default; no more pods;
  `render.twin_rooms` stays `one`; the `critical_cleared` acceptance, a sofa facing another group's coffee table when
  its own gets a new one, and real03's renumbered column ids are approved.
- **Final pass** (CPU only, §14.16): the sky default with re-pinned GPU checks, the recognition answer-store fix
  (exit code 2), the fix that keeps real02's L-1b sofas from turning into kitchen islands, more tools for a far
  armchair, the closed-door GPU test on twin rooms, one review fix. Full CPU suite: 5,865 passed, 0 failed
  (75 min).
- **Open for Milestone 14** (§14.17): the final images predate the last fix rounds (real03, real04) and the new sky
  (all three); one build-and-render pod (about $3-4) would show them. Unfixed P6c findings (see-through hall wardrobe,
  darker exteriors under the ground cap, paler sky behind the indirect clamp, agent and library items) and the open
  decisions of §14.13-14.15.

GPU cost of Milestone 13: $51.24 over 14 pods (estimate $46-54). Project total: **$181.78 of $300**. No pod is running.

### real04 rerun on the latest code (23 Oct 2026)

Your request of 23 Oct 2026: real04 again on a pod with the latest changes. Pod `udqp9w9972b08f` (RTX PRO 6000, 106
min, $4.40), code 2799c88 (windows-only sky default, final-pass fixes), polish off, 256 spp, 3 agent rounds, GPU tests.
Results: [`results/review/real04_rerun_20261023/`](../results/review/real04_rerun_20261023/).

- 42 views (37 interior, 5 exterior; P6a 49: the L1 koridor_2 / teras_2 twins and the blank `ext_front_entrance` are
  gone, as expected). Drawn anchors 40/40, accepted edits whose finding is gone 91 % (10/11), 0 interior views at EV ≥
  +5, EV gap 0.17 (P6a 0.67), last-round LG 4 (P6a 6), stage time 87 min (P6a 109).
- GPU tests: 45 passed, 2 failed, 9 skipped. Failures: white-balance tint 42.97 / 42.6 over the ±40 bound in L0
  e_yatak_odasi_2 / _3; f_L0_043 (abo_B07GFLG5MM) tagged "modern minimal", not the project style. Not fixed.

GPU cost: project total **$186.18 of $300**. No pod is running.

### 3D Warehouse layer, group options 10x, real04 ground floor (23 Oct 2026)

Your requests of 23 Oct 2026: add the 3D Warehouse GLBs of your Drive zip as a library source (relaxed mode only,
`commercial_safe: no`, licence not reviewed), keep every model ("cars, laptops, TVs, fences, whole kitchens ... think
bigger"), then grow the group furniture options 10x and use the ground-floor plan of real04 that matches the basement.

**3D Warehouse** (`wenart/assets/warehouse.py`, source `3dwh`, `GROWTH_ONLY=3dwh` in `scripts/jobs/library_growth.sh`):
3 pods, $12.40 in all (`9skbxiezc2eoac` $0.20: zip names broke the extraction; `e7pe2c4zku7hg2` $6.82: first audit;
`wf4crmtpkhro3a` $5.38: every model kept and audited, 0 vision answers left). 3,462 GLBs, 3,456 typed and fixed
(units: metres 2,569, feet 751, inches 110, cm 18, mm 8; up axis turned on 145), 6 dropped (broken GLB JSON).

| | models | keep | fix | removed |
|---|---|---|---|---|
| furniture (`entries`) | 1,977 | 929 | 214 | 834 |
| decor | 523 | 404 | 39 | 80 |
| extras: trees, doors, windows, objects (`extras`, new) | 956 | 737 | 117 | 102 |
| **all** | **3,456** | **2,070** | **370** | **1,016** |

- Most removals are sets and scenes (a sofa with its table and rug in one file), multi-object files and logos;
  the reasons per model are in [`results/library/audit/3dwh/audit.md`](../results/library/audit/3dwh/audit.md), the
  contact sheets per type in `results/library/audit/3dwh/contact/`.
- Top furniture types: armchair 238, corner sofa 159, sofa 123, double bed 120, chair 105, desk 97. Extras: 190
  untyped objects, 174 trees, 120 doors, 110 whole kitchens, 61 windows, 35 gates, 35 palms. The furniture fit does
  not read `extras` yet (the hooks for doors, windows and trees come later, as you said).
- Catalogue: `wenart/furniture/catalog_library.json` now has 3,932 furniture entries, 1,249 decor and 956 extras;
  every non-3dwh entry is unchanged. Every render that uses a 3dwh model says `commercial-safe: no`.
- GPU tests on the pod: 8 passed, 1 failed (a 5.09 m sectional over the flat 5 m size bound; the bound is now the
  type's largest product + 15 %, as the ingest allows).
- Please switch the Drive link sharing of the zip back off.

**Group options 10x** (`wenart/furniture/groups.yaml`): 263 options (26 before), two new groups (reading corner,
bedroom chest). New options carry an area window (`min_area` / `max_area`, `min_wall`, `min_width`) and are offered
beside the old ones; new partners (end tables, floor lamp, plant, pouf, dresser or TV on the facing wall, bookshelves
beside a desk) default to 0, so the old options build what they built. Drawn groups keep the old options; rooms with
drawn furniture get no reading corner or chest (completed, not added to); set extras (bath, hall) add only sizes
unless chosen; a bunk bed and a crib only on request. Solver fixes found on the way: required groups are never
dropped for optional ones, each group and option gets its share of the position budget, L/U kitchen corners are no
aisle obstacle (G8). real04's rooms (CPU dry run on its last building): no room fails the checks or loses a required
group; 9 s for all rooms.

**real04 ground floor**: the DWG draws the ground floor twice (r5 17.17 x 12.00 m, bulging out; r16 15.17 x 12.00 m,
the basement's size). The sheets stage now takes the drawing whose outline matches the adjacent levels as the base
and leaves the other out (`outline_mismatch` conflict, listed in the report); same-size copies and copies in other
documents stay as before.

**real04 with the new library** (pod `hpd4daiaklaefz`, RTX PRO 6000, 118 min, $4.90, code 0f15dbe, polish off, 256
spp, 3 agent rounds): [`results/review/real04_new_library_20261024/`](../results/review/real04_new_library_20261024/).

- Ground floor read from r16 (r5 ignored, conflict `sc_002`); 42 views (37 interior, 5 exterior); drawn anchors 40/40;
  0 interior views at EV ≥ +5.
- 44 of 236 built furniture pieces and 18 of 105 decor items use 3D Warehouse models; the most used model covers 5 %
  of the built library pieces (M12: 34 %), 114 distinct models; library quality ≤ 3 on 36 % (this morning 52 %).
- New group options in use: 1.40 m bed with nightstands, 1.00 m wardrobe, bookshelf with a plant, narrow bookshelf,
  bistro table with a plant. Bedrooms with a complete set 6/8 (this morning 8/8): the two 14 m² ground-floor bedrooms
  of r16 have one nightstand each. Accepted edits whose finding is gone 74 % (14/19; this morning 91 %, 10/11).
- GPU tests: 45 passed, 2 failed, 9 skipped (the same two kinds as this morning: white-balance tint 43.7 / 44.4 in L0
  e_yatak_odasi_2 / _3; one Poly Haven table tagged classic / rustic). Not fixed.
- Full CPU suite after the fixes of 87abeca: 5,855 passed, 0 failed (46 min).

GPU cost: 23 Oct $22.18, 24 Oct $4.90 so far. Project total **$203.48 of $300**. No pod is running.

**Before / after rule** (your rule of 24 Oct 2026): every before / after compares the project's Milestone 13 run with
the run that has the later changes. The Milestone 13 run of real04 (2799c88) is committed as the baseline in
`results/baseline/m13/` and is the default of `python -m wenart.report sheets13` / `metrics13`; real02 and real03 get
theirs (P6c, P6b) from the volume before their next run. The real04 review above already compares against it.

## real06 (24 Oct 2026): the user's DWG, read and rendered

The DWG (`projects/real06/real06.dwg`, AutoCAD 2004, no unit, no brief) stopped the first pod at the sheets stage
(pod `r00voo3mh1lz8b`, 6 min, $0.24). The reading code now handles what it showed, each rule general and tested
(`tests/test_real06_reading.py`, 15 tests):

| What the drawing does | Rule added |
|---|---|
| no unit, drawn in metres and shrunk to 1:50 (1 unit = 50 m) | a scaled unit (`m 1:50`) from level marks, dimension texts and door swings when no plain unit fits; marked inferred |
| nine drawings in a grid of frames drawn as four LINEs each | frame panels split the sheet |
| no drawing titles | plans by room names + door swings, elevations beside sections with rooms, roof plan by slope texts (`EĞİM%33`), plan levels by their floor marks |
| level-mark lines beside the section, nearly parallel roof lines | not read as terrain; no roof corner far away |
| dimension chains on their own layer pass for walls | dimension lines leave the wall choice on a dimension layer |
| wall piers with pilasters at the window jambs | a stepped run of short pieces is one wall |
| a two-panel sliding door drawn with lines, a door leaf narrower than its gap | read as doors |
| an entrance 0.50 m above the ground: handrails | `site_ramp` / `site_handrail` are known object kinds (the build stopped on them) |

real02/03/04 are unchanged (rooms, walls, areas; a few wall ends move 1-2 mm). Full CPU suite: 5,911 passed, 2 failed
(both already failing before, visible only with LibreDWG installed: real04's tree count, a pod-packing golden test).

**Library**: user decision of 24 Oct 2026: every project may use any library model (licence mode `relaxed` by
default; `CLAUDE.md`, `wenart/defaults.yaml`).

**Render** (pod `lrmdbppb3lr1c1`, 56 min, $2.31, code 36d1b20, polish off, 256 spp, default style):
[`results/review/real06_20261024/`](../results/review/real06_20261024/): 34 views (28 interior, 6 exterior), hip
roof, entrance steps with handrails. GPU tests 43 passed, 2 failed (depth over 60 m through bathroom windows; two
planned pieces hidden in bathroom views). Weak spots seen on the sheets: the ground-floor kitchen run is not in view or
not built, the dining area has small tables instead of the drawn round table, the facades carry many dark vertical
strips, the sliding doors are built as wooden slabs.

## Exterior upgrade (24 Oct 2026): facade, railing, library doors / windows / plants / cars, gutters, roof

User request of 24 Oct 2026 (real04 remarks, fixes general). Changes, each for every project:

| Remark | Change |
|---|---|
| walls look like blank concrete | `facade.FACADE_SCHEMES`: per style family a render colour, a basement cladding and a wood accent around the main entrance, when no drawing, brief or style names the facade (inferred faces) |
| a "balcony" bulge in the basement | inferred terrace guards: glass panels and posts instead of one steel slab |
| outside doors, new windows | `opening_models` / `opening_build`: one audited library model per category (entrance, door, glazed door, window) on the outer openings, panels side by side for ribbon windows, the scene glass, the style's frame colour on plain frames; `WENART_LIBRARY_OPENINGS=off` |
| plants, cars | `site_models`: library trees / palms / bushes per species (species words, crown words, kind), cars on drawn parkings (also a draped driveway up to 20 %); `WENART_SITE_LIBRARY=off` |
| rain gutters | an outlet from each gutter to its downpipe |
| roof | `roof.apply_override` refuses agent values the drawing gives (real04's drawn 32.5 / 11.3 degree mansard had been rebuilt at 45 degrees, 1.35 m too high); fascia board in the gutter look; ridge and hip caps |
| walls under the eaves read yellow | the lawn's bounced light is 75 % desaturated |

Pod `x884zdj3506zo3` (110 min, $4.55, code a7e0084): [`results/review/real04_exterior_20261024/`](../results/review/real04_exterior_20261024/),
before / after vs Milestone 13. GPU tests 47 passed, 9 skipped. Full CPU suite 5,935 passed; 2 failed, both failing
before (LibreDWG-only real04 tree count, the pod-packing golden plan). Open: the library bush rendered white (an opaque
leaf texture); fixed after the run (`vegetation.fix_plant_materials`), to be seen on the next pod run. Metric 13 (views
with >= 50 % bare wall) went from 9 to 13 in this run's interior views (agent rounds differ; not looked into yet).

**Follow-up (24 Oct 2026, user: "gaps" in the roof, "bulge at the side of the pool")**: the bulge was an assumed light well
made against the sloped ground where the drawn pool terrace lies under the sill (`site.wells_on_platforms`); the
roof's gaps were gutters running on along the roof terraces (`facade.eaves_edges`), and the assumed terrace parapets
rose over the eaves (now at the eaves line with a glass railing); library models the audit rated 2 or less are no
longer picked (the white bushes). Pods `37me6g1nvncmu1` (119 min, $4.94) and `xrsf17cw0e6od1` (109 min, $4.51):
[`results/review/real04_exterior_20261024c/`](../results/review/real04_exterior_20261024c/); GPU tests 48 passed.


## The architect, its answers and the top-down views (25 Oct 2026)

User requests of 25 Oct 2026 (general, every project): an "architect" that asks what an architect would ask and
fixes the plan; top-down views of every floor with the ceilings off; answers to the first questions; "the AI on the
pod must answer the questions and make the changes"; "don't restrict this to 16 questions: there might be 1000s".

| Request | Change |
|---|---|
| ask like an architect, about everything | `wenart/blender/architect.py` + `architect_rules.py`: 32 rules (arrival, access to terraces and pools, circulation, kitchen, stairs, every floor reached, daylight, windows to the outside, fresh air, low sills, privacy, room size / area / type / ceiling, openings in their walls, door widths, doors that lead somewhere, outer walls, furniture in its room, free doorways and windows, room to use each piece, falls, outside doors, light wells, rain water, trees). Each rule is asked of every element it applies to: real04 gets 572 questions; a big building gets thousands |
| a report that scales | `architect.md`: totals, one table row per rule (asked / fine / changed / answered / open), the open questions (major first, the first 150) with their answer keys and options, what changed; `architect.json` holds every answer; the scene manifest keeps only what is not fine |
| answers: "1 no, inside window should be outside; 2 yes; 3 yes" | `projects/real04/architect_answers.json`; `architect_actions.py` carries answers out on every run before anything is planned: the two windows between bedrooms move to the bedrooms' outer wall (same size), the play-room windows grow to 1/10 of the floor (4.0 m wide, a lower sill onto the terrace: the mansard roof stops the head at 1.71 m), the kitchens stay separate. Drawn values kept (`drawn_*`), changes marked `corrected_by_ai` / `adjusted_by_ai`; an answer acts only on the element at the place it names (ids change between readings) |
| the AI on the pod answers | `wenart/agent/architect_ai.py`, run by the scheduler before round 0: the agent model picks one choice per open question (strict JSON schema), code carries it out on a copy and asks every question again; kept only when its question is settled and no new major question opens; `keep` never settles a major question. Accepted answers: `orchestrator/architect_answers.json` (the build reads them through the build brief, so they enter the build fingerprint; the user's answers win); log: `orchestrator/architect_ai.md` |
| top-down: "from right up to left down, halve the walls" | `wenart/blender/topdown.py`: camera at the north-east looking south-west (azimuth 225), walls / doors / windows / railings cut at 0.6 m (was 1.2 m), furniture whole; exact-solver and bisect fallbacks where the fast Boolean failed; the labels draw every window as a blue line with its id, as built |

**No clashing furniture** (user note of 25 Oct 2026: "it's unacceptable to see clashing furniture at this stage"):
`wenart/blender/clashes.py`, run by `build.prepare` on every build (variants too): two pieces whose plan shapes
overlap more than 3 cm (an L sofa is its two parts) and whose heights meet are planned apart before anything is
built. Overlaps by design stay (a seat tucked under its table, a kitchen run's members, a basin on its unit, a
wall-hung piece). One object read twice is built once (real04: a cupboard read as its outline and as its "dolap"
block). The lesser piece gives way (accessory, then seating, then anchor; added before drawn) by the shortest way to a
free place in its room, clear of the doorways, at most 0.5 m (drawn) or 1 m; a table set moves as one; a seat stops
tucked; a bed or sofa never moves for a lamp; an accessory with no place is not built. Every change keeps
`drawn_footprint` and is reported by the architect (F5). real04: 23 clashes fixed on the base build (chairs through
tables, lamps in beds, lamps through lamps, ottomans under armchairs), 20 on the open-kitchen variant, none left. The
mesh check S2 had let them through (soft seats take 5 cm; open library meshes escape its ray test). The dark "table"
on real04's corner sofa is the model's own arm tray (3D Warehouse "sofá bandeja de braço"), not a second piece.

**Pod runs of 25 Oct 2026** (real04): `hc7yat1tfh1440` stopped after 18 min ($0.76) to restart with the clash fix;
`nrf83xxffuzj3g` (32 min, $1.31) stopped in the build: the AI architect had given the two windowless bedrooms of the
older reading new windows (its answers: enlarge the bedrooms' windows, keep the thin walls to the roof terrace) and
those windows carried a status the build refuses (fixed: `unverified`, as wide as the floor's other windows);
`8feaummqlo4zc1` (111 min, $4.59) ran the whole pipeline: 731 architect questions, 0 open; 2 clashes planned apart
(armchairs over their small tables); 4 of 56 GPU tests failed (three read `building_final.json` instead of the
building as built: now `scene/building_built.json`; one coffee table hidden behind a sofa). Its south rooms rendered
4-7 EV darker: the new odd-sized windows had swapped the building's window model to "Window1 1", whose panes are
an opaque picture of glass. A window model must now have see-through glass (`opening_models.glb_glass`, and a guard
when the model loads), and the model ranking takes the proportion error in steps of 0.05.

Final run `waqvtaiocrgu02` (123 min, $5.10: 2 % over its $4.98 worst case, the job ran to 116 min and the pod's
grace ran while the results downloaded; the runner had been cut by the session's 2-hour background limit and was
re-attached late, so most files were fetched afterwards: `pxsy2vhcgnqn7q` did not boot, $0.19; `dy1u0yky8kfk58`,
8 min, $0.33): [`results/review/real04_architect_20261025/`](../results/review/real04_architect_20261025/) (top-down
views, the architect's report, the AI's answers, before / after sheets and metrics vs Milestone 13). The aluminium
window is back; no interior view at +5 EV or more (metric 9 as in the baseline); 2 clashes planned apart, mesh cuts
all under 3 cm; GPU tests 45 passed, 1 failed (a classic / rustic library table in the modern play room), 10
skipped. After the run: the corner sofa "sofá bandeja de braço" (3D Warehouse) is removed from the library (its
built-in arm tray reads as a table through the sofa; the English-titled sofas and chairs with a table had been
removed by the audit); the next run picks another corner sofa. Open: bedroom 3's new north window keeps its views
darker (the lighting gives no fill light to a room with a window); metric 5 shows one nightstand per bed in bedrooms
3 and 4 and no fridge in kitchen 2 in this run's building (the fit and the agent's rounds, not the build).

Also: `RESTORE_OUTPUTS=1` in `scripts/jobs/full.sh` moves the pipeline outputs a failed pod set aside
(`/workspace/.repo-broken-*/outputs`) back into the repo's outputs (a move, never a delete).

## Terraces, details, taste, decor and the user's lessons (25 Oct 2026, not yet on a pod)

The user's notes of 25 Oct 2026 and what changed (CPU only so far; the next real04 pod run shows them):

| Note | Change (general, every project) |
|---|---|
| "This section is not making any sense" (ext_7: the east pool deck) | A terrace that doors or windows open onto takes a floor of their building (`site.floor_level`), never the mean ground between two floors; no front court is cut into a terrace; mirrored twins match (real04: sp_002 -1.40 -> -3.00 m, its twin sp_001's level; the copy's decks -> 0.00 m). A sunken terrace gets a flight of steps up into the slope (cheek walls, a hole in the ground), landing on paving where it can (the driveway). Retaining walls and sloped kerbs follow the ground (no saw-tooth); a wall holding the ground over 1.2 m carries a guard; stepped bands are planted and stop at drawn hedges and at each other. |
| "Is that table on the terrace ok? Suitable for the terrace? Is the door to the terrace ok?" | The fit ranks models made for outside first in open-air rooms (`fit.outdoor_grade`: teak, rattan, metal, "outdoor"; no desks with drawers or upholstery). A terrace door must be mostly glass (`opening_models.glb_glass_share` >= 45 %), else the glazed door in the windows' frame finish. Architect U1 (outdoor furniture: an inside piece the AI added is not built, a drawn one is asked: remove or retype) and D3 (terrace doors). |
| "Better architectural details, better internal stairs, better finishes in the fences on the parapets" | `wenart/blender/details.py`: balustrades of three kinds by the style (frameless glass in a channel with a cap rail; posts with glass bays on clamps and a round handrail; vertical bars at gaps under 0.11 m), a stone coping on roof-terrace parapets. Stairs: tread plates in the floor finish with 25 mm nosings over painted risers, a balustrade (balusters or glass) under a round handrail on every open side, a wall handrail on brackets where both sides are walls. Architect K1 (risers, goings, 2R+G, width): a U stair drawn with risers over 0.20 m (a drawing error no code allows: real04's four stairs, 11-12 lines for a 3 m storey, 0.25-0.29 m) gets winders in its half landing (`parametric.winder_treads`), its footprint as drawn: real04 0.175-0.176 m risers, 2R+G 0.63 m; the answer `stair_winders` with count 0 keeps it as drawn. K2 (guards, copings), K3 (one balustrade language). |
| "Pillows on beds and sofas seem floating" | Cushions lean 20 degrees on a sofa, 24 on a headboard, and sink 2 cm into the soft seat; the build drops a decor cushion on a model that has its own cushions or pillows (the decor stage had judged the provisional model). |
| "No taste in the furniture selection" | `wenart/furniture/taste.py`: every library model's wood tone, metal finish and colours are read from its GLB (cached on the volume); the fit fits a room's anchors first and ranks the rest by the room's set: one wood tone from the style and one contrast, one metal finish, loud colours only from the palette (design rules: 60-30-10, one dominant wood repeated, one metal per room). The vision critic gets D3 (a piece that does not go with the room: swap it). Architect S2. |
| "Not enough decor; furniture groups are not sufficient" | Long tops (sideboard, console, dresser, TV unit) take a group of three; every room is filled up to a styled minimum (living 9, bedroom 7, dining 4, kitchen and hall 2) from its empty slots in a stylist's order. Drawn groups are completed with accessory options too (end tables, a floor lamp, a plant, a bench, a dresser), never a second anchor; a re-solved group keeps the core options. Architect S3, S4. |
| "The architect should ask what I asked all along; use AI; keep developing" | `wenart/blender/architect_lessons.json`: 25 lessons from the user's requests and corrections, each with the rules that check it; architect.md gets "What the user taught me"; the AI architect's prompt carries them; on the pod the AI checks the lessons no rule covers yet (`orchestrator/architect_lessons.md`); `python -m wenart.agent.lessons add "<request>"` turns a new request into a lesson (with the agent model: a general lesson, its question and rules). |

## Before / after against the latest run (25 Oct 2026)

User rule of 25 Oct 2026: "From now on every run is against its latest run compare not according to milestones"
(it replaces the Milestone 13 rule of 24 Oct 2026; `CLAUDE.md`, lesson UL26).

| What | Change |
|---|---|
| which run is "before" | `wenart/report/latest.py`: the project's newest run older than the new one, from the runner's copies (`runs/<job>/results/final/<p>`, a fetch job's folder counts for the run it fetched; the most complete folder wins), the committed `results/baseline/latest/` and, when nothing newer is known, the Milestone 13 copy. A run without renders is skipped |
| reports | `python -m wenart.report sheets13` / `metrics13` take it by default (`--baseline m13` on request); each sheet's labels name the two runs ("before: run 20261025-115105-full") |
| keeping the latest run | `python -m wenart.report latest --out <run>/final/<p> --promote` copies the run into `results/baseline/latest/` (`runs.json` names it) after its report. Now there: real04 = job 20261025-115105-full, real06 = job 20261024-053145-full |

## real04 pod run with the 25 Oct details (25 Oct 2026) and the fixes it showed

Pod `s20y6p5bz1fx3w` (RTX PRO 6000, 113 min, $4.68, code 4ee8192; job 20261025-180008-full), compared with the
latest real04 run (job 20261025-115105-full, the new rule):
[`results/review/real04_details_run_20261025/`](../results/review/real04_details_run_20261025/) (41 before / after
sheets labelled with the two runs, metrics, top-down views, the architect's report, the AI's answers and lesson
check). All stages ok; GPU tests 46 passed, 1 failed (a bathtub planned at the edge of banyo_1's frame is not in its
index pass: a near miss of the frustum test, as in earlier runs), 9 skipped.

| Seen | Result |
|---|---|
| ext_7 east pool deck | one sunken terrace at the basement floor (-3.00 m) with a retaining wall, a guard and steps up into the slope; the saw-tooth bands are gone |
| terrace furniture | the turned-leg indoor table on the roof terrace is now a marble bistro table with outdoor chairs |
| stairs | tread plates with nosings over painted risers, a round handrail; 4 U stairs with 5-7 winders |
| complete room sets (metric 5) | 17 of 24 -> 19 of 25 (both kitchens, one more bedroom with two nightstands); living rooms still lack a TV unit |
| the AI architect | 14 of 14 open questions answered and carried out; the lesson check: 2 issues (decor, nightstands), 11 "unknown" |

Fixed after the run (general, tested):

| Problem | Cause | Fix |
|---|---|---|
| every glass balustrade (stairs, roof terraces, pool decks) rendered black | the thin glass's Fresnel node takes 1 / IOR on a back face, so past ~44 degrees the pane reflected everything (total internal reflection); a straight-on test had passed | the back face gets 1 / IOR so both faces reflect like the front (`materials.thin_glass_material`); `tests/test_blender_thin_glass.py` renders a pane at 0 and 75 degrees (was 0.03 % light through at 75 degrees) |
| the new corner sofa ("Sofa en L", 3D Warehouse) showed dark bands | a SketchUp export: each face has a copy on the same vertices turned the other way in a dark default colour (99 % of its faces); the two fight in the render | `furniture.separate_twins` moves each such face 0.2 mm along its own normal at import, so the copy facing the camera is the nearer one (every double-sided library model; a bed with the same doubling renders as before); `tests/test_blender_backfaces.py` |
| the AI lesson check said "unknown" for 11 of 13 lessons | it saw room names and furniture types only | each lesson carries what its code checks found (open findings first) from the review after the AI's answers; rooms carry their area, open-air flag and the models' wood tone and metal (`agent/lessons.py`) |
| 4 Blender tests failed since the details and clash work (not run in the last CPU pass) | the stair record listed 3 of its 4 materials; cushions sink 2 cm; the test showroom's library row overlapped the grid, so the clash planner moved it | the stair record lists the glass; tests updated; the library row sits below the grid |

## real06 pod run with the 25 Oct details (25 Oct 2026)

Pod `rcs1w840d63hxq` (RTX PRO 6000, 89.5 min, $3.71, code e83cf89; job 20261025-195332-full), compared with real06's
latest run (job 20261024-053145-full):
[`results/review/real06_details_run_20261025/`](../results/review/real06_details_run_20261025/) (34 sheets, metrics,
top-down views, the architect's report and the AI's answers). This run predates the glass, doubled-face and decor
fixes above. The AI architect answered 31 of 57 open questions (5 refused, 21 left for the user); the agent removed 19
findings in 3 rounds; mesh cuts deeper than 3 cm (S2) 10 -> 2; views of halls or bare walls 8 -> 7; drawn anchors 13 of
13 built as before. GPU tests 42 passed, 3 failed, 11 skipped: depth over 60 m in two bathroom views and two bathroom
pieces missing from the index pass (both as in the run before), and a library model of another style: the agent swapped
a toy-like generated washbasin (F1 out of scale, D2 crude) for an HSSD basin tagged modern / minimal in the
Scandinavian project (`swap_model` does not check the style; open).

Seen on the sheets: the bedroom now has two nightstands, a lamp, a rug and cushions that sit; the living room and the
kitchen had no decor at all (unverified rooms: fixed above, `decor.room_takes_decor`); the new glazed doors are a library
model with a busy black-and-white pattern (open: the glazed-door choice ranks by glass share only); the exterior tree is
a weaker generated tree than the olive of the run before (open); sun patches through openings clip white on the floor.

Full CPU suite with Blender on the path (25 Oct 2026, after the fixes above): 5,868 passed, 20 failed. One was caused
by the 20-degree cushion lean and is fixed (`rest.LEAN_FALLBACK_DEG`); the other 19 fail the same way on the code before
the 25 Oct details (5178a81): Blender look / variants / render / site / m11 exterior / m5 e2e / run e2e / doors-windows
tests left behind by earlier milestones' changes (ceiling material names, facade, roof ridges, pool coping, decor ids,
A/B controls), the golden run plan and real04's sheets test. Open: bring those tests up to date.

## What a visitor sees: the architect's defaults and the AI inspector (26 Oct 2026)

User notes of 26 Oct 2026 on real06's latest run: "why there is that many rain gutters, why the sink is so low, why
doors are up ... still with the furniture replacement it is not seen like a stylish house ... real06 windows second
floor: are the people going to jump off from it? ... I need ai models to see understand and fix everything before even
I look at it"; and: "fix should be general, it is not a fix for real06, it must be a fix for the project" (lessons
UL27-UL33, CLAUDE.md). Every cause was general; real06 only showed it:

| Seen on real06 | Cause (general) | Fix (every project) |
|---|---|---|
| doors 0.5 m over the floor | the section printed the ground floor "+0,50" (building z 0) while the plan's "+0,50" floor marks were read as z +0.5: the kitchen floor and its doors were built 0.5 m up; an upper floor's "+3,50" landing mark was taken for two ground-floor doors | one height frame: the section's printed ground-floor value is the zero of every relative plan mark (`levels.read.relative_zero`); a landing mark serves its own level's doors only; architect D4: a threshold over both floors snaps to them |
| 20 downpipes, 27 gutters | the roof outline followed every facade pier (70 points, crossing edges); one gutter and two pipes per run, spacing checked per run only (two pipes on one spot) | the eaves run straight past facade jogs under 0.6 m (`geom2d.close_jogs`, every wall face keeps 0.15 m of roof over it); downpipes planned for the whole roof: at the corners, at least 3 m apart, about one per 50 m2 (`facade.downpipe_plan`); A1 flags pipes too close and broken-up eaves. real06: 4 gutters, 3 pipes |
| basins at knee height, a bowl on the floor | the size table allows 0.10-1.20 m and the build stood every model on the floor | a wall-hung model hangs with its rim at 0.85 m (the fit sets `mount_bottom_m`, architect H1 checks and fixes), a bowl too shallow to hang alone is not taken |
| upper-floor doors and bare gaps into the air, two thin bars as "guard" | the architect's E1 offered only "keep"; bare gaps ("unclassified gap content") were built as holes; the facade's guard was two 40 mm bars | E1/O2: a door or gap with nothing outside on an upper floor is a window at the floor's sill by default (French window with a glass guard is the other choice); a bare gap onto the ground is a glazed door; every opening over a drop with a low bottom gets a frameless glass guard 1.10 m high across its width (`facade.guard_boxes`); W3's low sills too |
| no guard at the upper stair void | no code guarded a slab opening's edge | `details.void_guards`: a balustrade on every void edge off a wall and off the stair's arrival (K2 counts them) |
| a dressing room and a shower reached only "through windows" | windows between two rooms read for doors | W2: a window between two rooms where one has no door is its door by default; a dark room's window moves to its outer wall |
| dark six-panel doors, a black sash among white windows, a lattice glass | the opening models ignored the style; one model per opening; textured frames kept their colour; SketchUp's doubled panes | the style picks the look (clear glass, no panelled leaf in a modern house), one door and window family per building (else the parametric opening in the style's finish), the style's frame finish on textured frames, doubled panes made glass (`opening_models`, `opening_build`) |
| an empty kitchen | the drawn kitchen outline stayed untyped and unbuilt but still blocked the solver; a straight run needed 3.0 m of wall, a 5 cm jog broke the L corner; architect R2 offered only "keep" | an untyped unbuilt piece is no obstacle; outline jogs under 0.15 m are merged; compact fallback runs (I from 2.1 m, L legs from 0.9 m, a galley) with real module sizes; a kitchen left without a run is a critical finding (`solver.run_limits`, `layout.empty_kitchens`); real06's kitchen gets a galley with fridge, sink and hob |
| 4 "dining tables" with mismatched chairs in the living room | a second drawn table set was completed like the first; each chair fitted to its own drawn width (other models won); folding and "traditional" models ranked like the others | one dining group per room (`program.one_dining_row`; touching drawn tables merge), one model per role in a group (`fit.role_set_fit`), folding / camping / garden models last and dining models outside the style family's styles ranked down (`fit.misfit_of`, `style_mix_of`); (the reading of armchairs as table sets: see below) |
| a bedroom with no bed, a "kitchen counter" in it | a room with a zone was planned for its zone only; three nested outlines of one wardrobe read as a counter, a wardrobe and a cabinet; a straight run with nothing drawn on it typed a counter; "ODA" (room) read as bedroom | the rest of a zoned room keeps its room type's groups (`program.rest_place`); nested outlines are one piece (`reading.nested_outlines`); a counter needs a sink, a hob, an L/U corner or a kitchen block (`symbols.counter_run_evidence`); a room named only "room" takes the type of its agreed anchors (`reading.generic_rooms`) |
| armchairs read as "dining tables with chairs" | the table + chairs split took a seat cushion for a table and its arms for chairs | a seat-sized group whose parts hug the outline is one seat (`symbols.one_seat`); identical blocks get one type (`infer.same_block`); a round table ringed by 3+ seats is a coffee table; a wall type chosen by code needs its back on a wall (`infer.placeable`); a round piece is never a chair |
| the AI saw little of it | the architect offered "keep" only, so neither code nor the AI could act; the vision critic was never asked these questions; the final round never started (it was gated on the whole final stages) | the architect's safe defaults (`architect.defaults_of`, `build.prepare`; by: architect, the AI's and the user's answers win; 33 points settled on real06's last building); the visitor checks Q1-Q8 on every room and exterior view, routed to tools or to the stage that owns them; the final round asks every view again on the final renders and needs time for its own re-render only; `orchestrator/inspector.md` lists what the AI saw, fixed, handed on and left |

**The review of the 3D model itself** (user, 26 Oct 2026: "reviewing the 3d model itself could be better solution rather
than individual renders investigate decide apply"; lesson UL34). Investigated: the renders show what 34 cameras frame
(real06: rooms' far sides, facades and whole rooms never in a frame), and a vision model judging a height or a gap from
a perspective image guesses; the model as built holds every element with its place (`scene/building_built.json`, the
scene manifest's world box of every piece, the build plan and the facade kit). Decided: the model is reviewed first,
by measurement; the vision model looks at the model's floors from above and the renders only for the look. Applied:

| Layer | What | Where |
|---|---|---|
| the model measured (every element, every floor, before any render) | M1 doors on their floors and no floor step at a door; M2 working heights (basin, worktop, table, desk tops over the room's floor); M3 a guard before every low opening over a drop; M4 no upper-floor door or gap onto nothing; M5 rain water (pipe spacing, count per roof area, broken-up gutters); M6 one door and window model family per category; M7 rooms that make sense (anchors as built, one dining table per room) | `wenart/blender/model_review.py`; the build writes `scene/model_review.md`; the agent's code critic reads it every round (family `model`, each finding with a tool or the stage that owns it); the inspector's report leads with it |
| the model seen by the vision model | each floor's labelled top-down view of the final scene (angled, ceilings off, walls cut at 0.6 m, rooms named), rendered before the final round, with the visitor checks a floor shows (rooms that make no sense, pieces that repeat, clash or turn their back, a void with no guard) | `wenart.blender.cli topdown`, `scheduler.final_critical_rounds`, `critic_vision.critique_model_view` |
| the renders | the look: finishes, style, odd models, lighting, the camera | the vision critic's room and exterior checks (unchanged) |

On real06's model of 25 Oct (before today's fixes) the model review finds, in 0.6 s on the CPU: the doors 0.5 m up
(d_L0_002, d_L0_007, o_L0_001: floors 0.5 m apart with no stair), the basins with their tops at 0.10-0.57 m, 12 upper-floor
doors and gaps onto nothing, the kitchen with no kitchen, the 4 dining tables in the living room, two window models
and the "bedroom" with no bed (`tests/test_inspector_20261026.py`).

## The architect decides, entrances and doors that make sense (26 Oct 2026, second round)

The real06 run of the first round (pod `5fr7dp2g1co4sx`, 74 min, $3.08, commit b1be05a; sheets and reports in
[`results/review/real06_sense_run_20261026/`](../results/review/real06_sense_run_20261026/)) fixed what the user named:
3 downpipes instead of about 20, the upper-floor doors into the air are windows, the basins hang at 0.85 m, the kitchen has
its run and sink, the master bedroom has its bed and no dining tables. It also showed what was still wrong, and the user
added two requests: "make the AI architect a lot more smart and let it take decisions more" and, circling the entrance of
ext_4, "these sections not making sense, AI inspector needs to make sense of this" (lessons UL35, UL36). Every fix is
general; real06 is the test case.

| Seen on the run | Cause (general) | Fix (every project) |
|---|---|---|
| a 2.95 m flat oak slab in the facade that reads as a garage door, steps in front of it | a door with no library model became one flat leaf as wide as the opening | architect D5 "door types": an outside door from 1.4 m into a room is glazed (French doors up to 2.4 m, a glazed sliding door wider; a drawn sliding door stays sliding), the main entrance gets the entrance door, a garage door is sectional, a wide inside door has two leaves; `parametric.door_parts` builds glazed double, folding and in-frame sliding doors |
| handrails crossing in an X in front of the small door | two doors in the inner corner of an L facade each got a landing and four steps; the flights ran into each other; the "main entrance" was the widest door of the main facade (the 2.95 m garden door) | `site.entrance_layout`: doors whose landings or flights come within 0.6 m share one platform (the building cut out) with one flight and handrails along it only; a ramp keeps clear of every other door's approach; `levels.model.main_entrance`: a door marked as entrance, else a hinged 0.80-1.30 m door into a hall, ..., doors over 1.60 m last (real06: d_L0_004; real01-04 unchanged); model check M8 and visitor check Q9 |
| 3 armchairs read as 3 "dining tables" with 6 chairs (living room), 2 in the master bedroom | the armchair rule needed the arm pads within 3 cm of the cushion; the hand-drawn pads keep 2-5 cm off it | `symbols.seat_strip`: a thin strip against a side of the cushion's minimum rectangle over 60 % of it is an arm or a back (loose strokes of the same pad counted); real06: 7 armchairs; real02: 4 more armchairs; real01, real03, real04 unchanged |
| 6 of the AI architect's 9 picks "could not be done" and nothing more happened; the architect left 4 major points open | one pick per question, no second try; a default that failed ended the question | the architect's chains (a window that cannot move is a borrowed-light window, a high window into a bathroom; a doorway a drawn counter fills is a serving window; an AI-added piece gives way); a refused AI pick is asked again with the reason; the AI looks at each floor of the model and may change the architect's defaults or take decisions of its own, kept only when nothing new breaks |
| 22 of 39 critical code findings about doors that were windows | the critics read the building before the architect's changes | the critics read the doors and windows as built; the model checks are carried by the dry re-check, never "removed" |
| a third washbasin in the upper bathroom; a "TODDLER SINK" model; an orange glass sink; the ground-floor basin lost | the fit's wall-hung basins (`mount_bottom_m`) fell out of every "floor piece" filter, so the bathroom set missed its basin and added one; no product-use rule; the text "50" covered the basin's arc, which was dropped as a glyph | `schemas.off_floor` (fixed equipment hung below 1.0 m is a floor piece), a set never lacks a type the room has; `fit.use_misfit`: children's products only in a child's room, no kitchen / laundry / utility basins, no sanitary ware in a loud colour; `symbols.under_text`: a stroke chain under a text that closes a ring is drawing; `reading.wet_room_vanities`: in a wet room a counter with a basin is the vanity, never a kitchen (the full suite showed real03's vanities read as kitchens since the morning's counter rule) |

**The architect decides** (user: "make the AI architect a lot more smart and let it take decisions more"):

| Step | What it does | Checked by |
|---|---|---|
| chains of safe fixes (`architect.chain_of`, `build.prepare`) | an open point's default, then its fallbacks; a choice that could not be done is followed by the next; a default that opens a major point no fix settles is refused and the next is tried | the review after each round |
| retries (`architect_ai.answer_open`) | a refused AI pick goes back to the model with what it tried and why it failed, and the choices left (2 more tries) | carried out, settled, no new major point, the model review no worse |
| the look (`architect_ai.look`, after the first build) | each floor's labelled top-down view of the model, its open questions, the architect's major default decisions (confirm or change) and decisions of its own (`AI.<action>:<element>`: a door into the air becomes a window, a window between rooms a borrowed-light window, a room another type, a basin hung ...); the scene is built again when it decided | the same; an entrance is never made a window and a drawn piece never removed by a decision |
| the report | `orchestrator/architect_look.md`, `architect_ai.md` (every pick, accepted or refused with the reason), the architect's report lists the AI's own decisions (A0) | |

On real06's plan the architect now settles the four windows between rooms that stayed open (kitchen/living and
living/hall: borrowed-light glass; dressing/shower: a high window, sill 1.80 m).

Tests: the full CPU suite (6,200 tests in 4 shards, LibreDWG built in this session for the DWG tests) found
real03's vanities (fixed above) and `tests/test_sheets_real04.py::test_pools_terraces_parking_trees_and_marks`
(21 of 101 trees), which fails on the commit of 25 Oct too (open: not from today's work; the session's own
LibreDWG build may differ from the setup script's).

**The real06 run of the second round** (pod `gyuv033uvc1oqb`, RTX PRO 6000, 70 min, $2.90, commit 628424b; sheets against the
run of the first round, the architect's look and the inspector's report in
[`results/review/real06_decides_run_20261026/`](../results/review/real06_decides_run_20261026/); promoted as the latest):

| | first round (125412) | second round (170020) |
|---|---|---|
| critical findings, agent round 1 / final round | 49 / 41 | 18 / 15 |
| the review of the 3D model (M1-M8 failures) | (not yet on the pod) | 0 in every check |
| the architect's open points (major) | 7 (4) | 1 (0) |
| the AI architect | 9 questions, 3 answered, 6 "could not be done" | 2 answered; the look: 28 default decisions confirmed, 2 decisions carried out (a serving window over the kitchen counter, the unreachable dressing room a storage room), 11 refused (removals of drawn pieces: never by a decision) |
| ext_4 / ext_6 (the user's circles) | a 2.95 m oak slab with steps; handrails crossing in an X | a 4-panel glazed sliding door; one platform in the corner, one flight, handrails along it only |
| living room | 3 "dining tables" with mismatched chairs | armchairs, the corner sofa and ottomans, a coffee table |
| upper bathroom | 3 washbasins (a black utility sink) | the drawn basins, a wall-hung vanity, no third basin |

Still open after the run (for the next round): the living room's armchairs are of different models (a grey dining-style
armchair, brown leather ones, a red egg chair) and the vision inspector did not flag it (Q5); the child's room keeps two
large drawn beds (the AI wanted one gone; a drawn piece is never removed by a decision, so it is a question for the
user); the GPU test of the window panes' saturation fails at its edge (median 0.061 under 0.065; 0.068 in the run before:
the views changed with the new furniture; the panes show a pale evening sky, no haze); the real04 trees test (above).

## The big loop: the house fixes itself while it gets better (26 Oct 2026)

User, after the second round: "Results are not getting better enough, need a big loop that fixes itself for the
better" (lesson UL37). Investigated: every pod ran three agent rounds and one final round, then stopped with half an
hour of pod time left; the loop's measure was "findings removed", which never saw that the living room's armchairs did
not belong together or that a room was plain, and nothing compared the whole house before and after a change.
Decided and applied:

| Part | What | Where |
|---|---|---|
| the AI judge | every final render goes to the vision model as to the client's designer: `client_ready_score` 1-5, the Milestone 13 rubric tags plus `mismatched_set`, `not_stylish`, `makes_no_sense`, a note, and the problems that cost the points on element ids with a checklist check (routed to a tool or to the stage that owns it); `final/rubric_per_view.json` (metric 15 reads it) | `wenart/agent/judge.py` |
| the house score | 60 % the judge's mean (1-5 as 0-100), 40 % defects (10 points per critical and 3 per major finding of the code critic and the model review, 3 per open major point of the architect, per view, as 100 / (1 + points / 5)) | `judge.house_score` |
| the cycles | after the final renders: measure; then, while time is left (4 cycles at most): the final round on the critical findings, the visitor checks' and the judge's major ones; the changed views rendered again, the stages after the render again, the changed views judged again; a cycle that lowers the score by more than 2 is rolled back (its edits off, the views rendered again) and the loop stops; it stops too when a cycle gains less than 0.5 | `scheduler.final_critical_rounds`, `AgentLoop.measure` |
| the record | each cycle's score, the judge's mean, the critical and major counts, the verdict, the lowest-scored views | `orchestrator/big_loop.md` |

The loop around the pod runs (the session): each run is reviewed against the latest run, its general problems are
fixed in code with tests, and the next run starts; the first: drawn pieces of one set type in a room take one model
(`fit.role_sets`: the living room's six armchairs, three of them outside the seating group).
