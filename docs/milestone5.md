# Milestone 5 – Cycles look fixes, gated AI polish, final vision check

Goal: make the Cycles renders read as photos of the styled rooms (white walls look white, dark rooms are
readable), add an AI polish step that can only add realism and is thrown away when it changes geometry,
and check every final image with two vision models against the building JSON and the source plan.
Everything stays traceable: every polished image records its model, settings and gate metrics; every
vision-check verdict records both models' answers; nothing is auto-fixed.

All model ids, revisions, file names and APIs below were checked against Hugging Face, PyPI, the diffusers
0.40.0 wheel and a local Blender 5.2.2 on 2 Oct 2026 (§12). The spec was reviewed for contracts,
feasibility and the CLAUDE.md rules before implementation.

Scope:
1. Cycles look fixes (`wenart/blender`, `wenart/style/vocabulary.py`) (§2).
2. AI polish (`wenart/polish`): Z-Image-Turbo + Fun ControlNet Union 2.1, img2img with one control image,
   attempt ladder, sweep mode (§3).
3. Change gate (`wenart/gate`): edges lost and added, monocular depth, SAM 2.1 masks, colour, DINOv2
   features; calibration with benign and small/large negative controls (§4).
4. Final vision check (`wenart/vision_check`): expected elements from the building JSON and the
   object-index pass, the source-plan crop, two models, decoys, removal and insertion controls, realism
   preference (§5).
5. Style reference photos (`wenart/style/photos.py`) (§6).
6. Final report (`wenart/report`) (§7).
7. Pod jobs (`scripts/pod_setup_polish.sh`, `scripts/jobs/polish.sh`) and GPU tests (§8, §9).

Out of scope: TRELLIS.2 / Objaverse assets, the fine-tuned symbol detector, new recognition work.

## 0. Decisions (changes to `docs/plan.md` and `CLAUDE.md`)

| Before | Now | Why |
|---|---|---|
| plan §4.12: depth + canny control together | one control image per call (default depth from the Cycles Z pass; canny and geometry-edge controls in the sweep) | diffusers 0.40.0 has one `control_image`; `controlnet_conditioning_scale` is a plain multiply (a list fails) |
| plan §4.12: Z-Image ~16 GB, 2–5 s/image | bf16 weights 27.2 GB (transformer 12.3, Qwen3-4B text encoder 8.0, ControlNet 6.7, VAE 0.2): prompts are encoded first, the text encoder is freed, transformer + ControlNet + VAE stay resident (17.9 GiB); RTX PRO 4500 (32 GB) preferred | HF file listings; no CPU offload (it moves 19 GB per call) |
| plan §4.12: Depth Anything 3 `DA3MONO-LARGE` | `depth-anything/Depth-Anything-V2-Small-hf` (Apache-2.0) | DA3 is not in transformers; its PyPI package has unverified provenance and pins numpy<2; DAv2 Base/Large are CC-BY-NC |
| plan §4.12: edge IoU < 0.9 → reject | recall of reference geometry edges within 3 px (lost edges) + new straight lines on bare structure (added edges) | texture alone drops raw edge IoU to 0.47 (CPU experiment); recall stays 1.0; recall alone cannot see painted-on additions |
| plan §4.12: SAM mask vs index mask ≥ 0.95 | IoU(SAM on Cycles, SAM on polished); SAM vs index mask only as a reliability flag | same model on both sides cancels SAM's errors on thin legs |
| plan §4.13: frustum lists from `cameras.py` | expected elements from the index pass, cross-checked against the building JSON projected with a depth test | centre-in-frustum lists missed 39 of 140 (synthetic-01) and 64 of 213 (synthetic-03) visible elements; the index pass alone would be circular |
| plan §4.13: "the plan crop" | source-plan crop per view (page raster of the room's evidence, camera and elements drawn), shown next to every render in the report; as a second VLM image only if the A/B shows it helps | rule: compare with the building JSON **and** the source plan |
| plan §0/§4.5: photos of real rooms out of scope | used only as style references for slots the brief leaves open (§6) | M4 next step; no geometry from photos |
| CLAUDE.md: models into the Network Volume (`HF_HOME=/workspace/hf`) | container-disk cache `HF_HOME=/opt/wenart/hf` (plan §5 lesson since M2), M5 pods `--disk 130` | volume too slow for caches and venvs; downloads ≈ 1.1 GB/s. CLAUDE.md line updated, reported to the user |

## 1. Shared contracts (read before any area)

### 1.1 Paths and layout

- `--project-out` = `outputs/<p>` with fixed subfolders `scene/`, `renders/`, `controls/hide_<id>/`,
  `polish/`, `polish/sweep/`, `gate/`, `check/`, `final/`.
- Every file path inside an M5 JSON is POSIX and relative to the folder of that JSON.
- The job copies `results/furniture/<p>/building_final.json` to `outputs/<p>/building_final.json` when the
  volume has none; the build always reads `outputs/<p>/building_final.json`. `outputs/<p>/style.json` is
  always regenerated (deterministic) before the build.
- Readers take the building from `scene_manifest["building"]` (relative to the repo root) and the style
  from `scene_manifest["style_profile"]` (the profile that was rendered), never from a fresh `style.json`.
  The brief comes from `wenart.brief.load_brief(<project folder>)` (`building["project"]["source_folder"]`
  when present, else `projects/<p>`).
- Default config files (`polish.yaml`, `models.yaml`, `thresholds.yaml`, `check.yaml`) resolve relative to
  their package, never to the cwd.

### 1.2 `wenart/views.py` (shared view loader, written first; every area imports it)

Import-time dependencies: stdlib + numpy only (PIL imported inside the readers), so `render.py` can import
the encoders inside Blender.
- Encoders (used by `render.py`): `encode_depth_mm(z_m) -> uint16 HxW` (Cycles Z = planar depth along the
  view axis; round(z·1000); 0 where not finite, ≥ 1e9 or > 65.535 m); `encode_normal(n, hit) -> uint8
  HxWx3` (round((n + 1)·127.5); 0 where not hit); `encode_index(index_float) -> uint16 HxW` (rint, clip
  0..65535).
- Readers (PIL, never plain `cv2.imread`, which turns uint16 into uint8 BGR): `read_rgb(path) -> uint8
  HxWx3 RGB`, `read_index(path) -> uint16 HxW`, `read_depth_mm(path) -> uint16 HxW`, `read_normal(path) ->
  float32 HxWx3` (v/127.5 − 1; hit = any channel > 0). `write_png16(path, array)` / `write_png_rgb`.
- `View` (frozen dataclass): `camera, room_id, level_id, size (W, H), png, index, depth_mm, normal` (absolute
  paths), `index_stats: {int: {"pixels": int, "box": [x0, y0, x1, y1]}}`, `exposure`, `hidden`, `plugged`,
  `render_key`, `entry` (the raw manifest entry). `load_views(render_dir, cameras=None) -> dict[str, View]`;
  an entry without `render_key`, `index_stats` or `files.depth_mm/normal` raises `StaleRender` (callers skip
  that view with a warning).
- `index_table(scene_manifest) -> {pass_index: {"wenart_id" (proxy: stripped), "kind": door|window|
  furniture|decor (furniture_proxy → furniture; decor only for hostless decor such as plants), "type",
  "room_id", "room_ids" (openings), "host_decor": [types], "evidence", "status", "source", "box3d"}}`; the
  first manifest object with a pass index that is not hosted decor is the host.
- `regions(index, depth_mm, normal, table, pane_erode_px=6) -> Regions` with `masks: {region_id: bool HxW}`,
  `kinds: {region_id: kind}`, `pixels: {region_id: int}`, `background` (depth_mm == 0), `panes` (window
  index masks eroded by 6 px). Object region ids are the wenart ids; structure ids are `struct:floor`
  (nz > 0.9), `struct:ceiling` (nz < −0.9), `struct:walls` (|nz| < 0.3), all on index-0 pixels.
- `geometry_edges(index, depth_mm, normal, depth_rel=0.03, normal_deg=30) -> bool HxW` (1 px): index
  changes, relative depth jumps > 3 %, normal turns > 30°. The only definition, used by the polish geometry
  control and the gate's reference edges.
- Boxes: every pixel box in M5 JSON is `[x0, y0, x1, y1]`, x1/y1 exclusive. `box_to_1000(box, W, H)` =
  [floor(x0·1000/W), floor(y0·1000/H), ceil(x1·1000/W), ceil(y1·1000/H)]; back with
  `vlm_client.norm1000_to_pixels`.
- `project_paths(project_out) -> {scene_manifest, building_path, style_profile, project_dir, brief}`
  following §1.1.

### 1.3 Gate API (`wenart/gate/api.py`, re-exported by `wenart/gate/__init__.py` without importing torch)

- `Gate(thresholds=None, models=None, device="cuda")` (None → package `thresholds.yaml`; `models` a
  `gate.models.Models`, loaded lazily, fakeable).
- `Gate.prepare(view: View, ref_rgb) -> Reference`: regions, reference edges, Lab means and the model
  outputs on the reference (DAv2 disparity, SAM image embedding + masks for all object boxes in one batch,
  DINOv2 tokens), computed once per view and cached.
- `Gate.compare(ref, test_rgb) -> {"decision": "accept"|"reject", "reasons": [...], "notes": [...],
  "metrics": {...}, "gate_key": str}`; ValueError when `test_rgb` is not the view size.
- `decide(metrics, thresholds) -> (decision, reasons, notes)` is pure; used by `Gate`, `calibrate`, the polish
  ladder on reuse and `tests/gpu/test_polish.py`.
- Models stay on the GPU when `torch.cuda.mem_get_info()` shows ≥ 4 GiB free after the first attempt, else
  they are moved in per call; the polish frees its cache (`torch.cuda.empty_cache()`) before every gate call.
- `Gate.release_gpu() -> bool`: every loaded gate model to the CPU and per-call moves from then on
  (`resident: false`), then `empty_cache()`; a no-op without loaded models or off CUDA. The polish calls it
  after a CUDA OOM, before its single retry (§3.1).

### 1.4 Expected elements API (`wenart/vision_check/expected.py`; imports only stdlib, numpy, yaml, `wenart.views`, `wenart.geometry`)

- `expected_view(view, scene_manifest, building, cfg=None) -> {"camera", "room_id", "room_type", "size":
  [W, H], "elements": [...], "json_crosscheck": {...}}` (§5.1); elements sorted by descending pixels.
- `expected_views(project_out, render_dir=None) -> {camera: ...}`: pure; only the `expected` subcommand
  writes `check/expected_views.json`.
- `sweep_views(expected_views, n) -> [camera]`: the views with the most required elements, at most one per
  room, ties by camera name.
- `largest_required(expected) -> element | None` (used by the gate's CPU negatives and select-controls).

### 1.5 VLM calls (`wenart/recognition/vlm_client.py`, extended once)

- `build_request(..., images: list[str] | None = None)`: image parts in order, then the text; the
  single-image argument stays.
- `VLMClient.run_schema(images: list, prompt: str, schema: dict, *, seed=0, task="custom", max_side=None,
  labels: list[str] | None = None) -> VLMResult`: optional text labels interleaved before each image,
  jsonschema validation, no box conversion; on failure `data` is None and `error` is set.
- `client_factory(model_key, base_url)` returns an object with `.model` and `.run_schema`; fakes implement
  only those.
- `VLMClient.deadline` (epoch s, default None; the vision check sets `WENART_DEADLINE`): no request starts
  after it, each request's timeout is capped to the time left, and a retry pause that would end past it
  ends the retries. Images are sent as lossless PNG without the `optimize` pass (0.13 instead of 0.6 s per
  1600×900 image).

### 1.6 Model ids and revisions (single source)

Ids, revisions, files, allow patterns and licences live only in `wenart/polish/polish.yaml` (base,
controlnet) and `wenart/gate/models.yaml` (depth, sam, dino); `wenart/vision_check/check.yaml` holds the two
VLM ids. `scripts/pod_setup_polish.sh` reads these files and downloads exactly those; the loaders pass the
same `revision=`. Polish and gate run with `HF_HUB_OFFLINE=1` after setup. Every manifest records
`{repo, revision, licence}` per model.

| Role | Repo | Revision | Licence | Files / allow patterns | Size |
|---|---|---|---|---|---|
| polish base | `Tongyi-MAI/Z-Image-Turbo` | `f332072aa78be7aecdf3ee76d5c247082da564a6` | Apache-2.0 | `model_index.json`, `scheduler/*`, `text_encoder/*`, `tokenizer/*`, `transformer/*`, `vae/*` | 32.85 GB |
| polish control | `alibaba-pai/Z-Image-Turbo-Fun-Controlnet-Union-2.1` | `5155fc56d17821007d6f62ac192c09e0f0e72016` | Apache-2.0 | `Z-Image-Turbo-Fun-Controlnet-Union-2.1-2602-8steps.safetensors` | 6.71 GB |
| gate depth | `depth-anything/Depth-Anything-V2-Small-hf` | `5426e4f0f36572d16453bbda7a8389317b1bef99` | Apache-2.0 | `*.json`, `*.safetensors` | 0.10 GB |
| gate masks | `facebook/sam2.1-hiera-large` | `665f8e2ad61cf5f53d65644ff27c8ee525124610` | Apache-2.0 | `*.json`, `*.safetensors`, `*.txt` | 0.90 GB |
| gate features | `facebook/dinov2-base` | `f9e44c814b77203eaa57a6bdbbd535f21ede1415` | Apache-2.0 | `*.json`, `*.safetensors` | 0.35 GB |
| check pass 1 | `Qwen/Qwen3-VL-8B-Instruct` | `0c351dd01ed87e9c1b53cbc748cba10e6187ff3b` | Apache-2.0 | (vLLM) | 17.5 GB |
| check pass 2 | `zai-org/GLM-4.6V-Flash` | `411bb4d77144a3f03accbf4b780f5acb8b7cde4e` | MIT | (vLLM) | 20.6 GB |

The ControlNet config (591 bytes) is copied from `hlky/Z-Image-Turbo-Fun-Controlnet-Union-2.1@5d85f6a430fd40300f931bd1291e0c4982094859`
(a personal repo without a licence; the file is architecture metadata) into
`wenart/polish/configs/controlnet_union_2.1/config.json` with its sha256 and source, and passed as a local
`config=`. The Z-Image VAE is byte-identical to the FLUX.1-schnell VAE (Apache-2.0), not the FLUX.1-dev
licence.

### 1.7 Ownership (parallel implementation)

| Area | Owns |
|---|---|
| F0 foundation (first) | `wenart/views.py`, `vlm_client.py` additions, package skeletons with the §1.3/§1.4 signatures, the config files of §1.6, `tests/fixtures/style_photo_synthetic-03_salon.jpg` |
| A look | `wenart/blender/*.py` (materials, lighting, render, build, cli, schemas, shell where needed), `wenart/style/vocabulary.py`, the `walls.tint` removal in `profile.py`, the `style:` block of `defaults.yaml`, style fixtures, Blender tests, `tests/gpu/test_render.py` |
| B polish | `wenart/polish/*` |
| C gate | `wenart/gate/*` |
| D vision check | `wenart/vision_check/*` (incl. plan crops, controls selection) |
| E photos + report | `wenart/style/photos.py`, `wenart/style/__main__.py`, the `photo_terms` argument in `profile.py`, `wenart/brief.py`, the `brief:` block of `defaults.yaml`, `wenart/report/*` |
| F jobs | `scripts/pod_setup_polish.sh`, `scripts/jobs/polish.sh`, `scripts/pod_setup_recognition.sh` (parts switch), `scripts/pod_entry.sh` (deadline), `scripts/gpu_run.py` (if needed), `tests/gpu/test_polish.py`, `tests/gpu/test_check.py`, job tests |

## 2. Cycles look fixes (area A)

### 2.1 Window glass seen as glass only by the camera (`materials.py`)

`window_glass_material`: Mix Shader with factor = Math `MAXIMUM`(Light Path `Is Camera Ray`, `Is Singular
Ray`): Glass BSDF (IOR 1.45, roughness 0) for camera rays and singular rays (the camera ray refracted or
reflected by the pane, so both faces refract and the outside view stays in place), Transparent BSDF for all
other rays (diffuse, rough glossy, rough transmission, shadow). The old shader over-counted the sun 2.4×
and under-counted the sky (main cause of the orange cast). Depth and index passes still stop at the pane
(verified). Shower panels keep the M4 thin glass. Camera-only glass (the first M5 version) refracted only at
the room face and moved the outside view 23 px in 200 at 17°; `Is Transmission Ray` instead of `Is
Singular Ray` fixed that but left a second, misplaced reflection of a lamp and +20–53 % light behind a
frosted panel (Blender 5.2.2 probes, `tests/test_blender_glass.py`).

### 2.2 Albedo modes (`vocabulary.py`, `materials.py`)

Every `vocabulary.MATERIALS` entry gets `albedo_mode: "flat" | "texture"` and, for flat, `detail`.
- flat (colour from the vocabulary; the texture adds luminance detail only): plaster_white 0.35,
  plaster_cream 0.35, plaster_charcoal 0.35, plaster_exterior 0.5, painted_wood_white 0.5,
  painted_metal_white 0.15. Nodes (5.2.2 names): TexImage (sRGB) → RGBToBW → Math DIVIDE by the texture's
  mean luminance → Math MULTIPLY_ADD (x·detail + 1 − detail) → VectorMath SCALE of the flat colour →
  VectorMath MINIMUM (0.9, 0.9, 0.9) → Base Color. Normal and roughness maps unchanged.
- texture (wood, parquet, terracotta, marble, tiles, brick, carpet, concrete): texture colour with the
  mean-luminance gain clamped to 0.5..2.5 (was 0.5..4.0) and the 0.9 cap; `gain_clamped` recorded.
- The plaster entries of `WALL_TINTS` and the profile's `walls.tint` go (charcoal was darkened twice:
  albedo 0.027 instead of 0.05); update `defaults.yaml` (`style:` block) and the style fixtures.
- Material records gain `albedo_mode`, `detail`, `gain_clamped`.

### 2.3 Light portals (`lighting.py`)

One AREA light per window, RECTANGLE `size = width − 2·frame`, `size_y = height − 2·frame`, centred in
the opening, local −Z into the room, `light.cycles.is_portal = True`, manifest `kind: light, status:
assumed, reason: portal`. No fill light in rooms with windows (exposure makes dark rooms readable; the
documents say nothing about lamps).

### 2.4 Per-camera auto exposure and white balance (`render.py`)

Before each final render a metering pre-render: 1/8 resolution, 16 samples, no denoiser, no adaptive
sampling, persistent data on, Diffuse Direct / Indirect / Color passes on (off again afterwards), written to
a temporary EXR and read with Blender's OpenImageIO.
- Mask: no window pixels (index of any `wenart_kind == "window"` object), depth < 1e9, diffuse albedo
  luminance ≥ 0.02. Y = luminance(direct + indirect), block means over `width // 40` px blocks, Y50 =
  median of blocks with ≥ 75 % coverage.
- `view_settings.exposure = clamp(log2(target / Y50), lo, hi)` rounded to 1/6 stop (target 0.9, lo −2,
  hi +8; calibrated in run 0/1).
- White balance: illuminant = Σ(direct + indirect) over the mask, G = 1; whitepoint = illuminant^(1 −
  residual), luminance 1; residual per mood: warm daylight 0.35, golden evening 0.5, cool daylight 0.0,
  overcast 0.0, night 0.5; `use_white_balance = True`, `white_balance_whitepoint = whitepoint`.
- CLI: `--exposure auto|off|<EV>`, `--exposure-target`, `--white-balance auto|off|fixed:r,g,b`,
  `--look-from <render_manifest.json>` (per camera: the EV and whitepoint of that manifest's entry; exit 2
  when the camera is missing; recorded as mode `from` with the source). Controls always use `--look-from`.
- The mood comes from the scene property `wenart_mood` (build). View transform AgX, look None.
- Exposure and white balance change only the PNG/JPEG (verified); polish and gate use the PNG.
- Entry `exposure: {mode, ev, ev_raw, at_limit, target, incident_p50, whitepoint, wb_temperature, wb_tint,
  residual, window_clip_frac, meter_seconds, source}` (`window_clip_frac` = window pixels with all display
  channels ≥ 0.98).

### 2.5 Helper passes, index statistics, reuse key (`render.py`, `schemas.py`)

Per camera (via `wenart.views` encoders): `<cam>_index.png` now uint16; `<cam>_depth_mm.png` uint16 mm;
`<cam>_normal.png` RGB8 world normal; `<cam>_depth.png` unchanged (legacy, per-view normalised). Entry gains
`index_stats`, `files: {"depth_mm", "normal"}`, `render_key` = first 16 hex of sha256 over the JSON of
`{samples, resolution, denoiser, exposure mode/target/limits/look-from values, white balance mode, passes,
hidden, plugged, RENDER_CODE_VERSION}` (`RENDER_CODE_VERSION = "m5.2"`; m5.2: plugs take the wall faces'
materials, §2.6). `reuse_reason` also needs an equal `render_key`; entries without one are stale.
`RENDER_ENTRY` in `schemas.py` gains these fields (required for M5 entries).

### 2.6 `--hide`, `--plug`, `--hide-sets` (`render.py`, `cli.py`)

- `--hide ID[,ID]`: objects with `pass_index > 0` whose `wenart_id` (without `proxy:`) is listed get
  `hide_render = True` (frame + leaf, frame + glass, a piece with its decor). Unknown id → `unknown id`,
  exit 2. `--plug`: hidden doors/windows get a wall box closing the baked-in hole (wall from the opening's
  `wall_id`, extent from the hidden objects' world vertices on the wall axis, thickness + 4 mm, the wall's
  material slots, pass index 0; each face across the wall takes the slot of the wall face around the hole
  on its side, so a wet room's tiles continue on the room side and the exterior plaster outside; top,
  bottom and end faces slot 0; the info records `materials: {left, right, ends}`). Windows are plugged,
  doors are not (an empty doorway is not a door).
- `--hide-sets 'cam:idA;cam:idB+plug;...'`: all controls of a project in one Blender process (hide → plug →
  render the one camera into `<out>/hide_<id>/` → undo); the reuse check runs before rendering.
- Manifests record `hidden` and `plugged` (top level and per entry); `cli.render(..., hide=, plug=,
  hide_sets=, look_from=, exposure=, white_balance=)`.

### 2.7 Build fingerprint and manifest additions (`build.py`, `cli.py`)

- `build_fingerprint`: sha256 of the building file, the style file, this project's asset entries (the ids
  referenced by the style and the building, sorted JSON without fetch times), the file hashes of
  `wenart/blender/*.py`, `wenart/style/vocabulary.py`, `wenart/furniture/catalog.json`, and the build
  arguments. `cli build --reuse` (Python `reuse=False` default) skips Blender when `scene.blend` and the
  manifest exist and the fingerprint matches (prints `BUILD_REUSED <fp>`).
- `scene["wenart_mood"]`; `preview_maps: {<level>: {png, bbox_m: [x0, y0, x1, y1] (area actually covered),
  m_per_px, resolution}}` (pixel u = (x − x0)/m, v = (y1 − y)/m); the old `previews` key stays.
- Every door/window entry gets `room_ids` (rooms whose polygon edge carries the opening, from
  `cameras.room_openings`); every furniture/proxy/decor entry gets `box3d: {center: [x, y, z], size: [w, d,
  h], rotation_deg}` (world box as built).

## 3. AI polish (area B)

### 3.1 Loading and memory (no CPU offload)

1. Prompts first: tokenizer + text encoder (`Qwen3Model`, bf16, cuda) in a `ZImagePipeline` shell;
   `encode_prompt(<all prompts of the run>, device="cuda", do_classifier_free_guidance=False)`; embeddings
   kept on the CPU; then the encoder is deleted, `gc.collect()`, `torch.cuda.empty_cache()`.
2. `ZImageTransformer2DModel.from_pretrained(..., subfolder="transformer", dtype=bf16, device_map="cuda")`
   (FP32 shards cast per tensor), `ZImageControlNetModel.from_single_file(file, config=<vendored dir>,
   dtype=bf16).to("cuda")`, VAE on cuda (`enable_tiling()` above 1.5 MP), scheduler from the repo;
   `ZImageControlNetPipeline(scheduler, vae, None, tokenizer, transformer, controlnet)`. Resident ≈ 17.9 GiB.
3. `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`. On a CUDA OOM: one retry, still resident, after the
   `except` block (the failed call's frames and tensors are freed first), after the runner's release hook
   (`Gate.release_gpu()`) and `gc.collect()` + `torch.cuda.empty_cache()`; a retry that runs out of memory
   again is raised, and later OOMs of the run are raised at once. No `enable_model_cpu_offload()`:
   `ZImageControlNetModel.from_transformer` shares the transformer's embedders and first parameter
   (`x_pad_token`) with the ControlNet, so the per-model offload hooks left the transformer blocks on the CPU
   and every later ControlNet attempt failed; with the text encoder gone offload saves nothing either.
The manifest records `memory_mode` (always `resident`), `peak_vram_gib`, `seconds_per_forward`,
`load_seconds`, `oom_retries`.

### 3.2 img2img with one control image

- `full = get_default_z_image_sigmas(8)`, `t_start = int(max(8 − min(8·strength, 8), 0))`, `tail =
  full[t_start:]` (empty → error); `scheduler.set_timesteps(sigmas=tail)`; σ0 = `scheduler.sigmas[0]`
  (shift 3: strength 0.125 → 1 step from σ 0.30, 0.25 → 2 from 0.50, 0.375 → 3 from 0.643, 0.5 → 4 from 0.75).
- Latents: VAE encode of the render (`retrieve_latents(..., sample_mode="argmax")`), `(x − shift_factor)·
  scaling_factor`, then `σ0·noise + (1 − σ0)·x0` with a CPU generator seeded per attempt.
- Call `pipe(prompt=None, prompt_embeds=[emb.to("cuda")], control_image=..., controlnet_conditioning_scale=
  s, height=H, width=W, sigmas=tail, num_inference_steps=len(tail), latents=latents, guidance_scale=0.0,
  generator=g)`; H and W always explicit (the pipeline defaults to 1024×1024 and stretches the control).
- `mode: anchor` (sweep only): `ZImageControlNetInpaintPipeline.from_pipe(pipe)`, `image=render`, all-black
  `mask_image` (keep everything), same tail/latents. `role: presumed_bad` (sweep only): strength 0.75, no
  control, `ZImageImg2ImgPipeline.from_pipe(pipe)`.
- After every attempt and before gating, the Cycles pixels are pasted back into every window pane (index
  mask eroded 6 px, 3 px feather): the outside view is always the Cycles HDRI (`panes_restored: n`).

### 3.3 Size

`size: native` reflect-pads 1920×1080 by 4 px top and bottom to 1920×1088 and crops back; `size: WxH`
(multiples of 16, e.g. 1536x864) resizes with Lanczos and back. The gate always compares at the render size.

### 3.4 Control images (`controls.py`, numpy/PIL/OpenCV, CPU-tested)

- `depth` (VideoX-Fun convention, near = bright): valid = depth_mm > 0; vmin = p2, vmax = p85 of valid
  depths; x = 1 − clip((d − vmin)/(vmax − vmin), 0, 1); invalid → 0; uint8 RGB.
- `canny`: `cv2.Canny(gray(render), 100, 200)` white on black, RGB.
- `geometry`: `views.geometry_edges(...)` dilated to 2 px, white on black, RGB.
Written once per view as `<cam>_control_<type>.png`, padded/resized like the render.

### 3.5 Prompt (`prompt.py`)

English, one paragraph, no negative prompt: `"Photorealistic interior photograph of a {room words} in
{family} style. {wall words} walls, {floor words} floor{, furniture list}. {mood} light through the
windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm lens."` Words from the
rendered style profile (slug → words table), room type from the building JSON, furniture list = own-room
required and optional furniture of the view (`expected_view`), deduplicated types, at most 8, by area.

### 3.6 Ladder, decisions, resumability

- `polish.yaml: ladder` = ordered attempts `{strength, control, scale, size, mode}`; default before
  calibration `[0.375 depth 0.8, 0.25 depth 0.8, 0.125 depth 0.8]` (native, plain). Attempts run in order,
  each gated at once; the first accepted attempt is the view's candidate; none → `final: cycles`, reason
  `gate`. Seed = `polish.yaml: seed` (0) + attempt number. Brief `polish: false` → all views `final:
  cycles`, reason `brief`. Room rule after the ladder: the candidates of one room must have wall-region Lab
  means within ΔE 5 of each other; otherwise every view of the room takes the strongest rung accepted by all
  of them (or Cycles) and the manifest says so.
- `attempt_key` = sha256 of {strength, control, scale, size, mode, seed, steps, sigmas, prompt, control PNG
  sha256, source PNG sha256, model repos/revisions/files, POLISH_CODE_VERSION, torch/diffusers versions}.
  A reused attempt keeps its PNG; its gate metrics are reused when `gate_key` (GATE_CODE_VERSION, gate model
  revisions, reference sha256) matches and no check of them carries an `error` (a model that failed, e.g. an
  OOM or a missing snapshot, is computed again instead of staying a reject), else recomputed; the decision
  is always recomputed from the stored metrics with the current `thresholds.yaml` (`decide`), then the
  ladder outcome is recomputed.
- `--deadline` (default env `WENART_DEADLINE`, epoch seconds): no new attempt starts after it; the manifest
  gets `"incomplete": true`; exit 0.

CLI:
- `python -m wenart.polish run --project-out outputs/<p> [--views all|cam,...] [--out DIR] [--force]
  [--deadline S]` → `<out>` (default `outputs/<p>/polish/`): `<cam>_a<k>.png`, `<cam>_control_<type>.png`,
  `<cam>_a<k>_preview.jpg` (≤ 300 KB, final attempts only by default; the attempt PNGs are written with
  zlib level 1 + RLE, lossless, and hashed from the encoded bytes), `<cam>_a<k>_gate.jpg` debug image
  (§4.4), `polish_manifest.json` (rewritten after every attempt), `polish_report.md`, and
  `determinism.json` (the `polish.yaml: determinism_view` polished twice with the same seed:
  `{camera, max_abs_diff, seconds}`).
- `python -m wenart.polish sweep --project-out outputs/<p> --views auto|cam,... --grid sweep|<file>` → every
  combination on every view, each gated, no early stop, into `polish/sweep/` (`kind: sweep`, attempts carry
  `role: grid|presumed_bad`). `--views auto` = `expected.sweep_views(..., n=4)` per project. Grid (10 combos
  + presumed-bad): strength {0.125, 0.25, 0.375, 0.5} × depth; {0.25, 0.375} × {canny, geometry}; 0.375 ×
  depth × 1536x864; 0.375 × depth × anchor; all scale 0.8.
- `python -m wenart.polish smoke --project-out outputs/<p> --views cam,... ` → 4 settings per view, timings.

`polish_manifest.json`:
```json
{"schema_version": "0.1", "kind": "run|sweep|smoke", "project": "synthetic-01", "incomplete": false,
 "models": {"base": {"repo", "revision", "licence", "files"}, "controlnet": {...}, "gate": {...}},
 "config": {}, "thresholds": {}, "device": "...", "torch": "...", "diffusers": "...",
 "memory_mode": "resident", "peak_vram_gib": 0, "load_seconds": 0, "seconds_per_forward": 0, "oom_retries": 0,
 "views": [{"camera", "room_id", "source_png": "../renders/<cam>.png", "source_sha256", "prompt",
            "controls": {"depth": "<cam>_control_depth.png"},
            "attempts": [{"k", "role", "strength", "control", "scale", "size", "mode", "seed", "steps",
                          "sigmas", "seconds", "diffusion_seconds", "cpu_seconds", "png", "sha256",
                          "attempt_key", "panes_restored",
                          "gate": {"decision", "reasons", "notes", "metrics", "gate_key"}, "debug_jpg"}],
            "final": "polished|cycles", "final_attempt": 1, "reason": "null|gate|brief|room|error"}],
 "rooms": {"<room_id>": {"rule": "ok|downgraded", "rung": 2}}, "warnings": []}
```

## 4. Change gate (area C)

### 4.1 Inputs and regions

Reference = Cycles PNG, test = polished PNG (both display-referred, render size), plus the view's uint16
index, depth_mm and normal maps; regions from `views.regions` (§1.2). Background is excluded everywhere;
window panes are excluded from edges, depth and colour (their pixels are the Cycles pixels after §3.2).

### 4.2 Checks (`thresholds.yaml`)

```yaml
edges:       {hard: true,  global_min: 0.95, region_min: 0.85, region_min_ref_px: 200, radius_px: 3,
              canny: {sigma: 1.5, low: 25, high: 75}}
added_lines: {hard: true,  region_max_len_frac: 0.04, min_len_frac: 0.04, unmatched_frac: 0.70}
depth:       {hard: true,  global_max: 0.02, region_max: 0.05, region_min_frac: 0.01}
masks:       {hard: true,  region_min: 0.90, region_min_frac: 0.005, sam_reliable_min: 0.70}
colour:      {hard: true,  global_max: 10.0, region_max: 15.0, region_min_frac: 0.01}
neutral:     {hard: true,  region_max_dchroma: 5.0}     # wall/ceiling regions of albedo_mode flat
features:    {hard: false, region_min: 0.80, region_min_frac: 0.01}
calibration: {source: null, date: null, separability: {}, accepted_shortfall: null}
```
`*_min`: value ≥ threshold passes; `*_max`: value ≤ threshold passes; `region_min_frac` = region pixels /
(W·H).
- edges: reference = `views.geometry_edges` kept where Canny on the reference (gray → Gaussian σ → Canny
  low/high, L2) has an edge within `radius_px`; recall = share of reference pixels with a test Canny edge
  within `radius_px` (`cv2.distanceTransform`); global and per object.
- added_lines: on structure regions (panes excluded), `cv2.HoughLinesP` segments of the test Canny edges
  with length ≥ `min_len_frac`·W whose pixels have no reference Canny edge within 3 px over ≥
  `unmatched_frac` of their length; value = total unmatched length / W per region (a painted frame, shelf
  or window on a bare wall). A segment pixel also counts as matched by a reference Canny edge at 0.2× the
  thresholds within 3 px whose gradient orientation is within 10° of the segment normal (`lines.REF_FACTOR`,
  `ANGLE_TOL_DEG`; optional keys `added_lines.ref_factor` / `ref_angle_deg`): plank seams and tile grout
  that the render shows just below the thresholds are not new lines once the polish makes them crisper,
  while a rug outline or stripe painted across them still is (any low-threshold edge would blind the check
  on textured floors).
- depth: DAv2-Small relative disparity on both images; test fitted to reference by least squares (scale +
  shift, 3 trimmed refits keeping 90 %) on valid non-pane pixels; error = mean |aligned − ref| / (p98 − p2 of
  ref); global and per object/structure region.
- masks: SAM 2.1 (one image encoding per image, all object boxes in one batch, `multimask_output=False`);
  IoU(SAM ref, SAM test) per object; objects with IoU(SAM ref, index mask) < `sam_reliable_min` are
  skipped as `sam_unreliable`.
- colour: CIELAB (D65, sRGB) mean per region, ΔE76; global = mean ΔE over valid pixels.
- neutral: |ΔC*ab| (chroma change) of wall/ceiling structure regions when the rendered wall/ceiling
  material is `albedo_mode: flat` (white must stay white).
- features: DINOv2-base patch tokens (518×924, no centre crop), cosine per patch, mean over patches ≥ 50 %
  inside the object; becomes hard when calibration separates it.

Metrics shape (every check the same): `{"<check>": {"global": float|null, "regions": {"<id>": float},
"skipped": {"<id>": "too_small|sam_unreliable|no_reference_px"}}, "regions": {"<id>": {"kind", "pixels"}},
"seconds": {"<check>": float}}`. `reasons` (hard failures) and `notes` (soft): `{check, region:
"global"|<id>, value, threshold, op: ">="|"<="}`. Decision: `accept` iff every hard check passes.

The pure parts (regions, edges, recall, added lines, fit, depth error, Lab/ΔE, chroma, IoU, decision,
controls) are numpy/OpenCV, CPU-tested with synthetic arrays; the model parts are thin wrappers with lazy
`torch`/`transformers` imports in `gate/models.py`.

### 4.3 Calibration (`calibrate.py`, `controls.py`)

- Views: the sweep views (4 per project) + 4 more per project (`sweep_views(n=8)`).
- Benign (must be accepted; CPU from the Cycles PNG): exposure ±0.3 EV (linear light), white balance
  ×(1.03, 1, 0.97), Gaussian blur σ 1, JPEG q 75, unsharp mask, local contrast ×1.5 (σ 6: crisper texture),
  Gaussian noise σ 3/255 (8 per view).
- Negatives (must be rejected): CPU, on `largest_required` and one more required object: shift 6, 12 and
  25 px (cut by the index mask, pasted, hole filled with `cv2.inpaint` TELEA), scale ×1.04, ×1.08, ×1.15,
  rotation 2°, erase; a window/door crop from another view pasted onto a wall region; colour: white balance
  R×1.15/B×0.85, wall region b* +10, floor L* −15. GPU: every `--hide` control (reference = normal render,
  test = hidden render: real removal) and the reverse (reference = hidden render with its own passes, test =
  normal render: real insertion).
- Presumed-bad (reported only): the sweep's `role: presumed_bad` attempts.
- `python -m wenart.gate calibrate --project-out outputs/<p> [--deadline S]` → `gate/gate_calibration.json`
  `{benign|negative|presumed_bad: [{camera, control, magnitude, decision, reasons, metrics}], rates:
  {benign_accept, negative_reject, by_control: {...}}, per_metric: {<check>: {worst_benign, best_small_negative,
  best_negative, separates, proposed}}, smallest_detected: {shift_px, scale}, explanations: [...]}` and
  `gate_calibration.md`. Proposed hard threshold = worst benign value + 25 % of the gap to the best small
  negative (never midway to the gross ones). Proposals are applied to `thresholds.yaml` by hand after review;
  a proposal looser than §4.2 needs the user's OK.

### 4.4 Debug image

`polish/<cam>_a<k>_gate.jpg` (≤ 300 KB): Cycles | polished (top), missed reference edges red + added lines
blue over the polished image | depth error heat (bottom), failing regions outlined with id and value.

## 5. Final vision check (area D)

### 5.1 Expected elements per view (`expected.py`)

From `views.View.index_stats` + `scene_manifest` + `building`: for every index v > 0 of the view:
`index, wenart_id, kind` (door, window, furniture, decor = hostless decor), `type`, `source`
(from_documents|added_by_ai|rule), `status`, `own_room` (furniture: room_id is the camera's room;
openings: the camera's room in `room_ids`), `pixels, area_frac, box_px, box_1000, touches_border`,
`visibility` (furniture/decor: `box3d` projected with the pinhole formula of `cameras.py`: in-frame share ×
min(1, pixels / in-frame hull area)), `evidence`, `role`:
- `ignore`: area_frac < 0.002;
- `required`: kind in {door, window, furniture}, own_room, (area_frac ≥ 0.03 or (area_frac ≥ 0.01 and
  (visibility is None or ≥ 0.35)));
- `optional`: everything else (decor and other-room elements are never required).
Unverified pieces and type `unknown` are listed as "furniture piece (type unverified)": only present/absent
counts for them. Thresholds in `check.yaml`.

Building-JSON cross-check (non-circular): every door, window and furniture piece of the camera's level is
projected (oriented box from footprint, height and rotation; openings from wall + offset + height) and
depth-tested against depth_mm (a sample is visible when within 5 cm of the rendered depth). `json_crosscheck`
lists `in_json_not_rendered` (projected visible share ≥ 0.35 and projected area ≥ 0.01, index absent),
`rendered_not_in_json` (index id with no building element), `misplaced` (the element's own index pixels,
put back into the world with depth_mm, lie more than `misplaced_margin_m` 0.10 m outside its drawn footprint
(furniture) or wall rectangle (doors, windows) for more than `misplaced_max_outside` 10 % of them; elements
with fewer than `misplaced_min_pixels` 20 are not judged; pieces use the height the scene built, the
manifest `box3d`). These are mismatches of the Cycles render, never auto-fixed.

### 5.2 Source-plan crop (`plan_crop.py`)

Per view `check/<cam>_plan.jpg` (≤ 300 KB): the source page of the room's evidence (the floor-plan page of
the camera's level: `building.documents[].pages[]` with that `level_id` and a `transform_to_building`;
rasters from `wenart.ingest.debug_image.raster_from_pdf/dxf/image`), cropped to the room polygon + 0.5 m
through the inverse of `transform_to_building`, with the camera, its view cone (24 mm, 36 mm sensor) and
every expected element's box (id, type, source) drawn. Always shown next to the render in the report. As a
second VLM image ("Image 2 (source floor plan of this room, for orientation)") only in the plan A/B of the
calibration, which favours the crop only if removal detection rises and false alarms do not
(`plan_ab.favours_plan`). `check.yaml: plan_image` (default false; set by hand after the A/B) sends the crop
as Image 2 with every element check of a camera that has one (`used` / `adopted` in `plan_ab` = this switch;
the report says "A/B favours the plan crop: set plan_image: true to adopt" until then); otherwise the report
says "source plan compared through the evidence chain, the projected cross-check and the side-by-side crop".

### 5.3 Prompt, schema, request

One call per (image, model). Labels E1..En by descending area for required + optional elements, plus one
sentinel decoy label shuffled in deterministically (sha1 of camera): type = first allowed type of the room
type absent from the room and from every list of the call (fallback armchair, desk, bookshelf, bathtub),
box = a 0.18W × 0.25H window over bare structure (index 0, ≥ 98 %) of the camera's normal render, 5 % steps,
lowest-centre tie-break; one box per camera on every image kind (it is bare on the removal, insertion and
swap images too). Line: `- E3: tv_unit (low long cabinet / sideboard); expected inside box [83, 674, 362,
933][, cut by the image edge]`. The prompt defines
the statuses, says an empty doorway without a door leaf is NOT a door, and excludes only walls, floor,
ceiling and the outside view from extras.

Schema per view (compiles in xgrammar 0.2.1): `{"elements": {E1: ELEM, ...} (all required,
additionalProperties false), "extras": [≤ 8 {category, box (0..1000), confidence}], "door_count": int
0..20, "window_count": int 0..20}`; ELEM = `{status: present|different|absent|unsure, seen_as:
CATEGORIES + nothing, confidence 0..1}`; CATEGORIES = door, window, building furniture types (without
unknown), plant, cushion, book_set, lamp, textile, other_furniture, other_object, generated from the schema
enums. Class of a category: door, window, furniture (incl. floor/table lamp, other_furniture), fixture
(lamp on wall/ceiling), decor (plant, cushion, book_set, textile, other_object). Post-validation normalises
inconsistent answers to `unsure`.

### 5.4 Two models and verdicts (`combine.py`)

Pass 1 Qwen3-VL-8B-Instruct, pass 2 GLM-4.6V-Flash, independent, one server at a time (port 8001, fp8 and
8192 context below 40 GB, `--limit-mm-per-prompt '{"image":2}'`, GLM `--reasoning-parser glm45`,
`VLLM_USE_FLASHINFER_SAMPLER=0`). Per element: present+present → ok; absent+absent → missing;
different+different → changed; absent+different → missing_or_changed; present vs absent/different →
disputed; with unsure → the other pass, `unverified`; a failed call → `not_computed` (never absent); a pass
that answers the decoy present → `unreliable` for the view. Extras: drop those ≥ 50 % covered by any indexed
mask of the image shown (insertion: the normal render without the target's pixels); A/B matched by IoU ≥ 0.3
and the same class → confirmed; decor extras are info. Counts: expected range [required, required +
optional + ignored]; a mismatch needs both models outside it on the same side.
Single model (`CHECK_MODELS` with one key): every result `unverified`, view verdict `info`, `single_pass:
true`, advisory. added_by_ai mismatches are labelled "added_by_ai: render/polish issue, not a document
conflict".

### 5.5 Calibration, controls, decision

- Baseline: every Cycles view, both models: FA_missing, FA_extra (views with a confirmed non-decor extra),
  count error rate, decoy acceptance per model.
- `select-controls` → `check/controls.json` `{"schema_version": "0.1", "controls": [{"id", "index", "kind",
  "camera", "room_id", "plug", "area_frac", "source", "dir": "controls/hide_<id>"}]}` (per project up to 3
  furniture with ≥ 1 from_documents, 3 windows, 2 doors; required own-room, area_frac ≥ 0.03, not touching
  the border, one per room and per id, largest first) and prints `CONTROL\t<id>\t<camera>\t<0|1>\t<dir>`.
  A control whose render is missing or still contains the index is dropped, not an error.
- Removal: hidden render vs the original expected list (must be absent/different). Insertion: the normal
  render vs the list recomputed from the hidden render (must report an extra covering ≥ 50 % of the
  element's box). Type swap: one required furniture type replaced in the list (sofa↔bed_double,
  armchair↔desk) must come back different/absent.
- Targets (`check.yaml`): combined FA_missing ≤ 5 %, FA_extra ≤ 10 % of views, removal flagged ≥ 80 % and
  confirmed ≥ 60 %, insertion ≥ 60 %, decoy acceptance ≤ 10 % per model. A missed target makes the check
  `advisory` for absolute flags; an advisory check is an open item that needs the user's OK before the
  milestone is called done.
- Decision (differential, active even when advisory): a polished candidate is rejected (`final: cycles`,
  reason `vision_check`) when an element that is ok/unverified on its Cycles render is confirmed
  missing/changed on the polished one, or a confirmed furniture/fixture/door/window extra appears that the
  Cycles render lacks (`added_by_polish`); a polished view with a not_computed or unreliable pass →
  `final: cycles`, reason `check_incomplete`. A mismatch confirmed on the Cycles render itself marks the
  view `needs_review` in the report.
- Sweep mode: element checks on the Cycles views, the controls and the plan A/B set; polished sweep
  attempts get only the realism preference, for the 2 best gate-accepted settings per view.

### 5.6 Realism preference (`preference.py`, info only)

Both models, both orders: "Which image looks more like a real photograph of a room?" `{"choice":
"first|second|same", "confidence"}`; a polished image is `preferred` when ≥ 3 of 4 answers pick it.

### 5.7 CLI and files

`python -m wenart.vision_check expected|plan-crops|select-controls|run|preference|combine|calibrate|style-photo
--project-out outputs/<p> [--model-key qwen|glm --server URL] [--kinds cycles,polished,controls,plan_ab]
[--deadline S]` with `main(argv=None, client_factory=None)`. Image kinds: `cycles`, `polished`,
`removal:<id>`, `insertion:<id>`, `swap:<id>`, `plan_ab:<cam>`, `sweep:a<k>`. Files in `check/`:
`expected_views.json`, `<cam>_plan.jpg`, `answers_<slug>.json` (`{model, slug, calls: {<call_key>: {camera,
image_kind, prompt_kind: check|preference|plan_ab, prompt, raw_text, data, latency_s, error}}}`, rewritten
after every call in call-key order, resumable by `call_key`; `run` and `preference` send `check.yaml:
calls.workers` (2; `--workers`, the job passes the server's `--max-num-seqs`) calls at once and wait for none
past `--deadline`: a call still running then is left unanswered for the next run, the file gets `incomplete:
true`), `check_manifest.json` (`{schema_version, project, advisory, single_pass, models: {<key>: {id, slug,
revision}}, views: {<camera>: {<image kind>: {verdict: ok|mismatch|info|not_computed, elements: {<wenart_id>:
{label, role, source, passes: {<key>: {status, seen_as, confidence}|null}, result}}, extras: [...], counts:
{...}, unreliable: [<key>], image_sha256: [<sha256 of each image sent>]}, "json_crosscheck": {...},
"polished_rejected": bool, "polished_reasons": [...], "needs_review": bool}}}`), `check_calibration.json`
(`{metrics, targets, missed: [...], advisory, plan_ab: {...}}`), `check_report.md`, `<cam>_<kind>_check.jpg`
debug images (expected boxes coloured by verdict: ok green, missing/changed red, disputed orange, unverified
grey dashed; decoy box; confirmed extras; `id type source` labels; ≤ 300 KB).

## 6. Style reference photos (area E)

- `wenart/brief.py`: `load_brief(project_dir) -> {"values": flat dict, "assumed": [keys]}` from
  `brief.yaml` + the `brief:` block of `defaults.yaml` (gains `polish: true`, `style_photos: []`).
- Photos live in `projects/<p>/style_photos/` (the ingest classifier reads only top-level files).
- `read_style_photo(path, clients: {"qwen": c1, "glm": c2})`: one pass per model (independent), temperature
  0, strict schema with vocabulary enums: floor (8 slugs), walls (5), light mood (5), family (9), each plus
  `unclear`. Values both models agree on (and not unclear) become terms with evidence `{method: ai, model,
  pass, file}`. `python -m wenart.vision_check style-photo` runs one pass with the current server and appends
  to `<out>.json` (a pass without data is an error, never `ok`, and is asked again on the next run; a call
  still running at the deadline is left for the next run); `python -m wenart.style.photos combine <json>
  --out <terms.json>` agrees the passes.
- `profile_from_brief(brief, photo_terms=None)`: photo terms fill only slots the brief text does not name
  (the slots that would otherwise be assumed from the family word or the defaults); the brief always wins;
  each use is listed in `matched_terms` as `photo:<file>:<term>` and in the warnings.
  `python -m wenart.style projects/<p> --out ... [--photo-terms <terms.json>]`.
- GPU check: in the check phase each model reads `tests/fixtures/style_photo_synthetic-03_salon.jpg` (a copy
  of the M4 render: charcoal walls, polished concrete floor); `check/style_photo_test.json` must give walls
  plaster_charcoal and floor concrete_polished.

## 7. Final report (area E)

`python -m wenart.report final --project-out outputs/<p>` (and `report sweep` in sweep mode) writes
`outputs/<p>/final/`: `final_manifest.json` (per view: camera, room, final image path, `polished|cycles`,
reason (gate|brief|room|vision_check|check_incomplete|error), the chosen attempt's settings and gate
summary, vision-check verdicts for both images, json cross-check, preference, exposure, ids per source and
the unverified pieces in view), `<cam>_final_preview.jpg` (≤ 300 KB), `<cam>_plan.jpg` copies,
`contact_<level>.jpg` (480 px tiles, label camera + `P`/`C` + `U<n>` unverified pieces, ≤ 300 KB), and
`final_report.md`: summary table (views, polished, Cycles by reason, mismatches, needs_review, advisory
flags, exposure range, seconds per stage from the manifests), per-view table, every mismatch with source and
evidence (never auto-fixed), the unverified items and conflicts of `building.json`, rooms mixing polished
and Cycles views, and the model/licence table from the manifests. The final image is polished iff polish
`final == polished`, the vision check did not reject it (§5.5) and the check saw those pixels: the sha256 of
the polished PNG on disk (and of the current Cycles render) must be in the check manifest's `image_sha256`
(a re-polish writes new pixels under the same name); a manifest without hashes gives `check_incomplete`.
Links only to files in `final/`.

## 8. Pod jobs (area F)

### 8.1 `scripts/pod_setup_polish.sh`

`#!/usr/bin/env bash`, `set -Eeuo pipefail`, ERR trap, logs in `/workspace/logs/`, idempotent, timed.
- `/opt/wenart/image-constraints.txt` from `python3 -m pip freeze | grep -iE '^(torch|torchvision|torchaudio|triton)=='`;
  every install with `-c` (never replaces the image's torch). If torchvision is absent: `torchvision==0.24.1`
  (`--no-deps`, index `https://download.pytorch.org/whl/cu128`; the pair of torch 2.9.1).
- `/opt/wenart/venv-polish` (`--system-site-packages`): `diffusers==0.40.0 transformers==5.18.0
  accelerate==1.15.0 huggingface-hub==1.33.0 "safetensors>=0.8.0" opencv-python-headless==4.14.0.94
  "numpy>=2"` + the repo's CPU deps (`pod_requirements.txt` without its hub pin). Stamped good only after: a
  CUDA bf16 matmul; `sm_120` in `torch.cuda.get_arch_list()` on Blackwell; bf16 SDPA on [1, 30, 8320, 128]
  under `sdpa_kernel([FLASH_ATTENTION, EFFICIENT_ATTENTION])`; `torchvision.ops.nms` on CUDA; imports of
  `ZImageControlNetPipeline`, `ZImageControlNetModel`, `Sam2Model`, `Sam2Processor`,
  `AutoModelForDepthEstimation`, `AutoModel` and every `wenart.polish`/`wenart.gate` module.
- Downloads with `HF_HOME=/opt/wenart/hf` from `polish.yaml` and `models.yaml` (pinned revisions, allow
  patterns); `setup_polish.json`: sizes, seconds, free disk, `MemTotal`, `MemAvailable`, `nproc` (the
  host's: in a container `/proc/meminfo` and `os.cpu_count()` show the host, 251 GiB and 112 CPUs in run 0),
  `pod_limits` (cgroup v2 `cpu.max`, `memory.max`, `memory.current`, or the v1 files; CPU affinity; the
  thread budget and thread variables `polish.sh` exported), versions.
- Parts by phase: diffusion + gate models only when `polish`, `gate`, `tests`
  (`tests/gpu/test_polish_backend.py` loads the polish models) or `smoke` is in `POLISH_PHASES`;
  `scripts/pod_setup_recognition.sh` with `RECOG_SETUP_PARTS="vllm models"` (new switch: skips PaddleOCR and
  LibreDWG) and `BAKEOFF_MODELS="Qwen/Qwen3-VL-8B-Instruct zai-org/GLM-4.6V-Flash"` only when `check` is.

### 8.2 `scripts/jobs/polish.sh`

Skeleton of `furnish.sh` (`run_stage`, `stage_failed`, `copy_results` after every stage and from the EXIT
trap, exit 1 when a stage failed) plus a background `copy_results` every 300 s under `flock`. Env:
`POLISH_PROJECTS` (default `synthetic-01 synthetic-03`), `POLISH_MODE` (`smoke|sweep|final`, default
`final`), `POLISH_PHASES` (default per mode: smoke `look polish check`, sweep `look controls polish gate
report`, final `look polish check report tests`; a check-only sweep run uses `check report tests`),
`RENDER_SAMPLES` (128), `FORCE_RENDER`, `FORCE_POLISH`, `CHECK_MODELS` (`qwen glm`), `SMOKE_VIEWS`.
`pod_entry.sh` exports `WENART_DEADLINE = start + MAX_RUNTIME_S − 900`; after it the heavy CLIs start
nothing new, and polish.sh skips the remaining heavy phases but still runs `report` and `copy_results`.

| phase | command (cwd `/workspace/repo`) | python |
|---|---|---|
| look | `$PY -m wenart.style projects/<p> --out outputs/<p>/style.json`; `$PY -m wenart.assets fetch --style ... --assets $ASSETS --size 2k` (all projects first); `$PY -m wenart.blender.cli build --building outputs/<p>/building_final.json --style outputs/<p>/style.json --assets $ASSETS --out outputs/<p>/scene --preview-samples 32 --reuse`; `$PY -m wenart.blender.cli render --scene outputs/<p>/scene/scene.blend --out outputs/<p>/renders --cameras all --samples $RENDER_SAMPLES --res 1920x1080 --exposure auto --white-balance auto [--force]` | `PY=/workspace/venv/bin/python` |
| controls | `$PY -m wenart.vision_check select-controls --project-out outputs/<p>`; `$PY -m wenart.blender.cli render --scene ... --out outputs/<p>/controls --hide-sets '<from the CONTROL lines>' --look-from outputs/<p>/renders/render_manifest.json --samples $RENDER_SAMPLES --res 1920x1080` | PY |
| polish | `$POLISH_PY -m wenart.polish run --project-out outputs/<p>` (final) / `sweep --views auto --grid sweep` (sweep) / `smoke --views $SMOKE_VIEWS` (smoke) | `POLISH_PY=/opt/wenart/venv-polish/bin/python` |
| gate | `$POLISH_PY -m wenart.gate calibrate --project-out outputs/<p>` | POLISH_PY |
| check | `$PY -m wenart.vision_check expected` and `plan-crops`; per model key: server up; `run` (+ `preference`; both `--workers` = the server's `--max-num-seqs`), `style-photo`; server down; then `combine`, `calibrate` | PY |
| report | `$PY -m wenart.report final|sweep --project-out outputs/<p>` | PY |
| tests | `$PY -m pytest -m gpu tests/gpu/test_render.py tests/gpu/test_check.py`; `$POLISH_PY -m pytest -m gpu tests/gpu/test_polish.py tests/gpu/test_polish_backend.py` (junit into the results; the backend test forces the CUDA OOM retry with the real models after the vLLM server stopped) | both |

The job exports `HF_HOME=/opt/wenart/hf`, `HF_XET_HIGH_PERFORMANCE=1`, and `HF_HUB_OFFLINE=1` after setup.
CPU threads: before the setup the job exports `OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS`, `MKL_NUM_THREADS`,
`NUMEXPR_NUM_THREADS`, `VECLIB_MAXIMUM_THREADS` and `OPENCV_FOR_THREADS_NUM` (OpenCV's own variable;
opencv-python-headless 4.14.0.94 ignores `OMP_NUM_THREADS`, checked 2 Oct 2026) = the pod's cgroup CPU
quota (`/sys/fs/cgroup/cpu.max` `<quota> <period>`, or v1 `cpu.cfs_quota_us` / `cpu.cfs_period_us`) rounded
up, at most `nproc`; `nproc` without a quota; `POLISH_THREADS` overrides (use it with the pod's vCPU count
if the log line `CPU budget:` shows no quota and the host's 112 CPUs). Every stage inherits them and the job
logs the value. Reason: in run 0b numpy/OpenBLAS, OpenCV and torch each started 112 threads (the host's
CPUs) under a much smaller quota and the gate's CPU work ran 10–50× slower.
`copy_results` mirrors the committed layout: `$RESULTS/renders/<p>/` (+ `controls/render.log`,
`controls/hide_<id>/`), `polish/<p>/` (+ `sweep/`, `smoke/`), `gate/<p>/`, `check/<p>/`, `final/<p>/`: JSON,
MD, `*_preview.jpg`, `*_gate.jpg`, `*_check.jpg`, `*_plan.jpg`, contact sheets (all ≤ 300 KB), log tails,
junit. Each copy takes only the files changed since the last copy (a stamp on the volume, set 2 s back for
1 s timestamps), many files per `cp`; the job's first copy and the copy from the EXIT trap take everything
(run 0b: ≈ 45 ms per file on the volume; copying every file after each of the 43 stages would have cost
≈ 25–40 min in run 2). From `/workspace/logs`, which every pod shares, only what this job wrote: its
`vllm-<key>.log`, `setup-polish-*.log`, `hf-download-*.log` and `setup_polish.json` (run 0/0b's results held
the M4 vLLM logs); `style_<n>.json` only when written together with this `style.json`.

### 8.3 Pod plan

Run with `scripts/gpu_run.py run --job scripts/jobs/polish.sh --gpu 'RTX PRO 4500' --disk 130 --grace <s>
--env POLISH_MODE=... --env POLISH_PHASES=...` (`RTX PRO 4000` when the 4500 has no stock; never L4).

Measured in runs 0 and 0b (RTX PRO 4500, 2 Oct 2026; the polish numbers still with the CPU oversubscription
that the thread budget of §8.2 is meant to remove; run 1a measures again):

| Step | Measured |
|---|---|
| setup | 4.4 min with the check part (venv 48 s, models 33 s, vLLM + VLMs 185 s); 1.3 min without it |
| look | ≈ 1 min with reused renders; a fresh render of 30 views ≈ 4 min (128 samples) |
| polish | 3.8 s per forward, 1–3 forwards per attempt (strength 0.125–0.375); ≈ 35 s per attempt (diffusion 6–24 s, gate 2–53 s) plus ≈ 90 s per view (gate reference, controls, PNG and debug writes): 489 s for 2 views × 4 attempts |
| check | vLLM start 140–290 s; 6.8–7.0 s per call, one call at a time |
| results | copy ≈ 45 ms per file on the volume (now only the changed files); the runner collects 0.81 s per file, one at a time |

| Run | Mode / phases | Purpose | Estimate |
|---|---|---|---|
| 0 | smoke: look (synthetic-01), polish smoke (2 views × 4 settings, gate inline), check (10 calls per model) | measure s/forward, VRAM, meter seconds, s/call; fix exposure defaults | done 2 Oct (runs 0 and 0b: 35 + 20 min) |
| 1a | sweep: look (both), controls, sweep, gate calibrate, report sweep | thresholds and ladder; polish and gate seconds with the CPU thread budget (`metrics.seconds` per check well under 1 s; per attempt `diffusion_seconds` vs `cpu_seconds`); the gate processors' CUDA uint8 input with `device=` (transformers 5.18) runs | ≈ 55–70 min |
| 1b | sweep: check report tests | check calibration, plan A/B, preference, style photo | ≈ 30–40 min |
| 2a | final: `look polish`, one project per pod (`POLISH_PROJECTS=synthetic-01`, then `synthetic-03`); the same command again until `polish/polish_manifest.json` has `incomplete: false` (attempts and gate results are reused) | the polished views | ≈ 2.5–3.5 min per view at run 0b's speed (90 s + 1.5–3 attempts × 35 s): synthetic-01 (30 views) ≈ 75–100 min, synthetic-03 (57 views) two pods; re-estimated from run 1a |
| 2b | final: `check report tests` (both projects) | vision check of the Cycles and polished views, final report, GPU tests | ≈ 75–85 min: setup ≈ 5 min; per model 3–5 min server start + (87 cycles + P polished + 2P preference calls) × 7 s ≈ 31 min at P ≈ 60; report and tests ≈ 5 min; again if the deadline cut it (the answers resume) |

Every pod must end before `WENART_DEADLINE` (start + 105 min of the 2 h cap); a pod the deadline cuts exits 1
and the same command continues from the volume. Run 2 is green when the last 2a pod of each project and the
2b pod exit 0. One pod for all of run 2 does not fit: at the measured speeds the polish of 87 views takes
3.5–5 h and the check of both models ≈ 70 min. `--grace`: 420 s for runs 0–1a; 840 s from run 1b on, whose
results hold 500–1000 files at 0.81 s each (840 s stays below the 900 s deadline margin), until
`gpu_run.py` fetches the results in parallel. Thresholds, ladder and check roles are set here in the session
from run 1's numbers (committed with the numbers). Each run gets its own gpu-log row; runs 1a–2b ≈ 8–9 pod
hours, ≈ $6 at $0.70/h (within $10 per day).

## 9. Tests

CPU (`pytest -m "not gpu"`):
- views: encoders/readers round trip (uint16 > 255, normals), regions, geometry edges, boxes, load_views
  with stale entries.
- Blender (skip without Blender): window glass (`tests/test_blender_glass.py`: the view through the pane stays
  in place, index/depth stop at the pane, one lamp reflection, interior light as through an open hole); flat
  albedo (white plaster within 0.03 of the flat colour, CV < 0.06 on a tiny render); portals (count, size, −Z
  into the room); metering on a tiny room (finite EV within the clamp, whitepoint); `--look-from`; render_key
  reuse; uint16 index; depth_mm/normal agree with the EXR; `--hide`/`--plug`/`--hide-sets` (index gone, depth
  at the wall, unknown id → exit 2; a plugged bathroom window shows the wall tiles on the room side); build
  fingerprint reuse; `room_ids`, `box3d`, `preview_maps` mapping.
- polish (fake pipeline, fake gate): sigma tails and σ0, pad/crop and resize round trips, controls, prompt,
  ladder, room rule, pane restore, resumability (attempt_key, gate_key, decision recomputed), deadline,
  `polish: false`, manifest schema.
- gate: regions, edge recall (25 px shift fails, texture noise passes), added lines (a painted frame
  fails), depth fit/error, Lab/ΔE/chroma, IoU, decide, every benign/negative generator, calibration
  proposal rule (25 % of the gap to the small negatives), fake models end to end.
- vision_check: expected elements and roles, json cross-check (a dropped and a moved element), projection
  against a known camera, decoy, schema strictness, post-validation, every row of §5.4, extras, counts,
  differential decision, check_incomplete, calibration metrics, preference, plan crop mapping, fake client
  end to end, resumable answers.
- style photos (fake clients, agreement, brief wins), brief defaults; report from hand-made manifests,
  contact sheet size.
- job scripts: `bash -n`, shebang, `set -Eeuo pipefail`, ERR trap, logs under `/workspace/logs`, stages,
  flags, venv per phase, deadline handling.
GPU (`pytest -m gpu` on the pod, reading files only): `test_render.py` (also: exposure recorded and within
the clamp, uint16 index stats consistent with `index_values`, synthetic-01 white plaster walls display R/B
≤ 1.10); `test_polish.py` (every view has a final image of render size; every accepted attempt passes every
hard threshold recomputed with `decide`; rejected attempts have reasons; manifests valid; benign accepted 100
% and negatives rejected ≥ 90 % unless `calibration.accepted_shortfall` names metric, rate and the date of
the user's OK; `determinism.json` max_abs_diff ≤ 2); `test_check.py` (≥ 95 % of calls answered per model;
calibration present; `advisory` set exactly when a target is missed; `style_photo_test.json` as §6);
`test_polish_backend.py` (the Z-Image backend's CUDA OOM retry with the real models: VRAM filled by the failed
call only, same image after the retry, no offload hooks, every pipeline works afterwards).

## 10. Done criteria

`pytest -m "not gpu"` green here; runs 0, 1a, 1b, 2 green on the pod; thresholds and ladder set from run
1's numbers and committed with them; previews, contact sheets, debug images, manifests and reports committed
under `results/renders/<p>/`, `results/polish/<p>/`, `results/gate/<p>/`, `results/check/<p>/`,
`results/final/<p>/`; `docs/plan.md` §4.12–4.13 and §8 updated per §0; `docs/progress.md` and
`docs/gpu-log.md` updated; every pod stopped. Open items that need the user's OK are listed in progress.md
(an advisory check, a looser threshold, an accepted shortfall).

## 11. Risks

- Polish speed is estimated (≈ 3 s per 1920×1088 forward on an RTX PRO 4000), not measured: run 0 measures.
- bf16 attention on sm_120 with torch 2.9.1: checked by the setup stamp before any model work.
- Low-noise starts (strength 0.125–0.375) are not documented for the 8-step ControlNet: the sweep decides.
- The vision models' yes-bias is unknown: decoys and the calibration measure it.

## 12. Sources (checked 2 Oct 2026)

- diffusers 0.40.0 wheel: `pipelines/z_image/pipeline_z_image_controlnet.py` (sigmas/latents/prompt_embeds,
  control encoding, 1024 default), `pipeline_z_image_img2img.py` (get_timesteps, prepare_latents),
  `pipeline_z_image_controlnet_inpaint.py` (mask semantics), `models/controlnets/controlnet_z_image.py`;
  METADATA (torch ≥ 2.6, huggingface-hub ≥ 1.23, < 2.0).
- Hugging Face API and model cards of every repo in §1.6 (licences, revisions, sizes); Z-Image-Turbo card
  (guidance 0, 8 forwards); ControlNet Union 2.1 card (control types, context scale 0.65–1.0, 8-step files).
- transformers 5.18.0 (PyPI; Sam2Model since 4.56.0); VideoX-Fun `comfyui/annotator/nodes.py` (depth and
  canny control conventions); vLLM v0.30.0 docs (multi-image, `--limit-mm-per-prompt`); PyTorch v2.9.1
  `.ci/manywheel/build_cuda.sh` (cu128 build includes sm_120).
- Blender 5.2.2 (local probes): view transforms and looks, white balance properties, `light.cycles.is_portal`,
  Render Result unreadable in background mode, EXR unaffected by view settings, shader node names, glass and
  portal light balance in a test room.

## 13. Integration notes (2 Oct 2026)

The six areas were merged into one branch; these are the decisions taken where the spec was silent,
ambiguous or contradicted itself, and the cross-area fixes. `tests/test_m5_e2e.py` runs every stage of
§8.2 on synthetic-01 (CPU, fake diffusion backend, real gate with fake models, an oracle vision client).

| Topic | Decision |
|---|---|
| §3.6 / §7 reasons | A Cycles view's reason can also be `deadline` (the deadline cut its ladder or the room rule; view `complete: false`) and, in the final report only, `not_run` (no polish run manifest, or the view is missing from it). Final-manifest reasons: `gate|brief|room|vision_check|check_incomplete|error|deadline|not_run`. |
| §3.4 control images | `<cam>_control_<type>.png` is written once at render size; every attempt pads or resizes it with the same size plan as the render. |
| §3.6 room rule | The common rung must be accepted by every candidate of the room **and** their wall Lab means must agree within ΔE 5 at it; rungs the early-stop ladder never ran are run on demand. Room entries also carry `views`, `candidates`, `delta_e_max`, `delta_e_after`, `incomplete`. |
| §3.6 resumability | A run that reuses every attempt loads no model; its manifest keeps `memory_mode`, `peak_vram_gib`, `load_seconds`, `seconds_per_forward` of the run that made the attempts (`stats_source: previous_run`). |
| §4.4 debug image | The polish writes `<cam>_a<k>_gate.jpg` with the gate's own `Gate.write_debug(ref, test_rgb, result, path)` (it reuses the maps of the last comparison). |
| §4.2 edges, added lines | Recall uses test-side Canny thresholds × 0.5 (`edges.test_factor`, default 0.5): with equal thresholds a white frame on a white wall vanished under the benign blur and −0.3 EV controls. Added lines are matched against reference Canny edges **plus** the view's geometry edges. Hough settings are code constants (votes = max(20, 0.5 × min length), gap 3 px, match 3 px). All three are calibrated in run 1a. |
| §4.3 / §5.5 `controls.json` | `dir` is relative to the project output (`controls/hide_<id>`, as §5.5 writes it), not to `check/` (§1.1); the file says so with `dir_relative_to: "project_out"`, and the gate calibration honours that key. |
| §5.2 plan A/B | Image kind `plan_ab:removal:<id>` is added, so the A/B can measure whether removal detection rises. |
| §5.5 `check_incomplete` | Also when the Cycles image's own check is not computed or unreliable (the differential decision needs both images). In single-pass mode nothing is confirmed, so the check never rejects. |
| §5.1 cross-check depth test | A sample is visible when nothing was rendered more than 5 cm in front of it (`z <= rendered + 0.05`; background counts as far); read literally, "within 5 cm" would hide dropped elements. |
| §6 brief | `load_brief` also returns `path` and `warnings`; `values` keeps nested blocks merged (`values["render"]["samples"]`), `assumed` lists dotted keys (`render.samples`). |
| §6 style photos in the job | The check phase agrees the project photos' passes into `check/style_photo_terms.json`; the next look phase passes it to `wenart.style --photo-terms` (empty terms change nothing). The vision check and the style module share one photo rule (`wenart.style.photos.style_photo_paths`). |
| §2.6 `cli.render` | Returns the out folder (not a manifest path) when `hide_sets` is given; the same ids asked with and without `+plug` in one call is a usage error (exit 2). |
| §2.7 build fingerprint | Also hashes `wenart/geometry.py` (the build's geometry depends on it). |

### 13.1 Review fixes (2 Oct 2026)

The M5 code review's confirmed findings were fixed in five groups (G1 polish, G2 gate, G3 Blender, G4
vision check and report, G5 pod jobs), each with a test that failed on the old code, and merged here. One
line per fixed finding (duplicate findings of the review share a line):

| Finding | What changed |
|---|---|
| G1 §3.1: the CPU-offload fallback for a CUDA OOM broke every later ControlNet attempt | `enable_model_cpu_offload` removed (the ControlNet shares the transformer's `x_pad_token`, so the hooks left the transformer blocks on the CPU). One resident retry after the `except` block, after `Gate.release_gpu()` and gc + `empty_cache`; a second OOM is raised and ends retries; `memory_mode` always `resident`, manifest `oom_retries`; `mem_available_gb` removed; schema enum without `offload`. Pod test `tests/gpu/test_polish_backend.py`. |
| G1 §3.6: stored gate metrics with a model `error` were reused, so a transient failure stayed a reject | `runner.gate_metrics_complete`: metrics are reused only when no check carries `error`; otherwise the stored PNG is gated again. |
| G1 §3.6: CPU side of one attempt (pod run 0b) | Attempt PNGs at zlib level 1 + RLE (lossless, ≈ 3× faster, same size), sha256 from the encoded bytes; attempts record `diffusion_seconds` and `cpu_seconds`. 1920×1080: 0.74–0.93 → 0.41–0.65 s per attempt. The 20–70× slower gate checks of run 0b are CPU oversubscription (G5 thread budget). |
| G2 §4.2: `added_lines` rejected polishes that only sharpen plank seams or tile grout | Oriented low-threshold reference matching (0.2× Canny, 10°, §4.2); benign control local contrast ×1.5 (§4.3); `GATE_CODE_VERSION` m5.2 (stored gate metrics are recomputed). Real Poly Haven floors: every benign control accepted (only local contrast ×2.0 on wood stays at 0.040), a painted rug outline still 0.62–0.95. |
| G2 §4.2: gate CPU cost per comparison (run 0b: colour 6–24 s, depth 8–11 s, features up to 17 s) | `layout.Layout` (valid pixels grouped by region, built once), `edges.EdgeIndex`, cached reference depth samples and DINOv2 norms; `models.py` sends a uint8 tensor to the device and resizes, normalises and upsamples there (`device=`). 1920×1080, 15 objects: compare 0.76–0.89 → 0.30 s CPU; metrics within 1e-4 of the mask-based functions. `Reference.lab` is float32 3×N over the valid pixels. |
| G3 §2.1: window glass moved the outside view (one-sided refraction) | Glass for `Is Camera Ray` or `Is Singular Ray` (Math MAXIMUM): the view stays in place, one lamp reflection, interior light 0.998 of the open hole; `tests/test_blender_glass.py`. |
| G3 §2.6: a plugged window in a wet room showed plaster | `Hider._plug` gives the plug the wall's slots; each face takes the slot of the wall face next to the hole on its side (`plug_face_slots`); `RENDER_CODE_VERSION` m5.2, so wet-room controls re-render on their own. |
| G4 §5.1: `misplaced` flagged correctly rendered beds, armchairs and windows | Containment test of the element's own pixels in world space (0.10 m margin, > 10 % outside, ≥ 20 px) with the built height (`box3d`); check.yaml keys replace `misplaced_frac_w`. synthetic-01 at 640×360: false flags 5 → 0, pieces moved 0.3–0.5 m caught in 11–28 → 24–40 of 41 piece-views. |
| G4 §5.3: the insertion control's decoy was placed on the hidden render and covered the element (2 review findings) | The decoy is placed on the camera's normal render for every image kind, type absent from both lists; insertion extras are dropped against the normal render without the target. |
| G4 §6: style-photo stored a failed pass as finished and logged `ok` (2 review findings) | A pass without data is an error and is asked again on the next run, also for records written before the fix. |
| G4 §7: the final report accepted a polished image the vision check never saw (2 review findings) | Check-manifest entries carry `image_sha256`; `decide` makes a view polished only when the polished PNG's (and the render's) sha256 is in it; no hashes → `check_incomplete`. |
| G4 §5.7: one stuck VLM call could run ≈ 30 min past `WENART_DEADLINE` | `run`/`preference`/`style-photo` wait for no call past the deadline (daemon threads, the call is left for the next run); `run` and `preference` send `calls.workers` (2) calls at once with one writer in call-key order. |
| G4 §5.2: plan A/B `adopted` was reported though the crop was never sent | `check.yaml: plan_image` (default false) sends the crop as Image 2 with every element check; `plan_ab` reports `favours_plan`, `used`, `adopted` (= used). |
| G5 §8.2: every stage re-copied all result files (≈ 45 ms per file, 25–40 min in run 2) | Incremental copy since a stamp on the volume (2 s overlap), many files per `cp`; the job's first copy and the EXIT-trap copy stay full. |
| G5 §8.3: run 2 in one pod could not end before `WENART_DEADLINE` | Run 2 split into 2a (`look polish`, one project per pod, repeated until complete) and 2b (`check report tests`); `--grace 840` from run 1b on; CPU thread budget = the cgroup CPU quota exported to every stage (`OMP_NUM_THREADS`, `OPENBLAS_NUM_THREADS`, `MKL_NUM_THREADS`, `OPENCV_FOR_THREADS_NUM`, …; `POLISH_THREADS` overrides). |
| G5 §8.2: results held earlier pods' logs and a stale `style_2.json`, and missed the control-render log | Logs and `setup_polish.json` only when written after the job's start stamp; `style_<n>.json` only together with this `style.json`; `controls/render.log` copied; `style.write_profiles` now removes `<stem>_<n>.json` extras of an earlier brief. |
| G5 §8.1: `setup_polish.json` recorded the host's RAM and CPUs, not the pod's limits | `pod_limits` (cgroup v2/v1 CPU quota, `memory.max`/`memory.current`, affinity, thread budget). The offload guard that read the host's `MemAvailable` is gone with the offload (G1). |

Contract requests between the groups, resolved at the merge:

| Request | Resolution |
|---|---|
| G1 → G2: a gate call that frees the GPU before the polish's OOM retry | `Gate.release_gpu()` / `Models.release_gpu()` (§1.3); the runner calls it through the backend's release hook. |
| G1 → jobs: run the backend's OOM-retry test on the pod | `tests/gpu/test_polish_backend.py` runs with `test_polish.py` in the polish venv after the check phase stopped vLLM; the setup downloads the polish models whenever `tests` is a phase (§8.1, §8.2). |
| G4 → `vlm_client.py`: a per-call wall-clock limit and a cheaper image encoding | `VLMClient.deadline` (§1.5), set by the vision check from `WENART_DEADLINE`; PNG without `optimize`. |
| G4 → jobs: workers to match the server on ≥ 40 GB cards | `polish.sh` passes `--workers` = the server's `--max-num-seqs` (2 below 40 GB, 4 above). |
| G5 → `wenart/style/profile.py`: stale extra profiles | `write_profiles` replaces its whole set (extras beyond the new count removed). |
| G2 → next pod run: confirm the device-side processors and gate seconds | Run 1a's purpose (§8.3). |
| G2 → `wenart/views.py`: `regions`/`geometry_edges` cost ≈ 0.35 s per view in `Gate.prepare` | Not changed: once per view (≈ 90 s per view on the pod, mostly oversubscription), and a float32 rewrite could move boundary pixels; revisit if run 1a shows it matters. |
| G5: the runner fetches results one file at a time (0.81 s per file) | Not changed: `--grace 840` covers 500–1000 files within the 900 s margin; a parallel fetch in `scripts/gpu_run.py` is an open item. |
