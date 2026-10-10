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
