# Milestone 5 – Cycles look fixes, gated AI polish, final vision check

Goal: make the Cycles renders read as photos of the styled rooms (white walls look white, dark rooms are
readable), add an AI polish step that can only add realism and is thrown away when it changes geometry,
and check every final image with two vision models against the expected elements. Everything stays
traceable: every polished image records its model, settings and gate metrics; every vision-check verdict
records both models' answers; nothing is auto-fixed.

Research behind every fact below (sources, file:line, measurements): the session notes summarised in
§10. All model ids, revisions, file names and APIs were checked against Hugging Face, PyPI, the diffusers
0.40.0 wheel and a local Blender 5.2.2 on 2 Oct 2026.

Scope:
1. Cycles look fixes (`wenart/blender`, `wenart/style/vocabulary.py`): camera-only window glass, albedo
   modes, light portals, per-camera auto exposure and white balance, extra helper passes, `--hide`/`--plug`.
2. AI polish (`wenart/polish`): Z-Image-Turbo + Fun ControlNet Union 2.1, img2img with one control image,
   attempt ladder, sweep mode.
3. Change gate (`wenart/gate`): edges, monocular depth, SAM 2.1 masks, colour, DINOv2 features, per object
   and per structure region; calibration with benign and negative controls.
4. Final vision check (`wenart/vision_check`): expected elements from the object-index pass, two models,
   decoys, removal and insertion controls, pairwise realism preference.
5. Style reference photos (`wenart/style/photos.py`): a VLM reads room photos into style vocabulary terms
   that fill only the slots the brief leaves open.
6. Final report (`wenart/report`): one report, manifest and contact sheets per project.
7. Pod job `scripts/jobs/polish.sh` + `scripts/pod_setup_polish.sh`, GPU tests `tests/gpu/test_polish.py`,
   `tests/gpu/test_check.py`.

Out of scope: TRELLIS.2 / Objaverse assets, the fine-tuned symbol detector, new recognition work.

## 0. Decisions taken in this spec (changes to `docs/plan.md`)

| Plan said (§4.12 / §4.13) | Now | Why |
|---|---|---|
| depth + canny control together | one control image per call (default depth from the Cycles Z pass; canny and geometry-edge controls in the sweep) | diffusers 0.40.0 has one `control_image` and no Z-Image multi-ControlNet; `controlnet_conditioning_scale` is a plain multiply (a list fails) |
| Z-Image ~16 GB, 2–5 s/image | bf16 weights 27.2 GB (transformer 12.3, Qwen3-4B text encoder 8.0, ControlNet 2.1 6.7, VAE 0.2) → `enable_model_cpu_offload()` on 24 GB cards; speed measured on the pod | HF file listings |
| Depth Anything 3 `DA3MONO-LARGE` | `depth-anything/Depth-Anything-V2-Small-hf` (Apache-2.0) | DA3 is not in transformers; its PyPI package has unverified provenance and pins numpy<2; DAv2 Base/Large are CC-BY-NC |
| edge IoU < 0.9 → reject | recall of reference geometry edges within 3 px | texture alone drops raw edge IoU to 0.47 (CPU experiment); recall stays 1.0 |
| SAM mask vs index mask ≥ 0.95 | IoU(SAM on Cycles, SAM on polished) ≥ threshold; SAM vs index mask only as a reliability flag | same model on both sides cancels SAM's own errors (thin legs) |
| vision check frustum lists from `cameras.py` | expected elements from the object-index pass | the centre-in-frustum lists missed 39 of 140 (synthetic-01) and 64 of 213 (synthetic-03) visible elements |
| HF cache `HF_HOME=/workspace/hf` (CLAUDE.md) | `/opt/wenart/hf` on the container disk (plan §5 lesson); M5 pods get `--disk 130` | the volume is too slow for venvs; downloads run at ≈1.1 GB/s; M5 models total ≈79 GB |

## 1. Cycles look fixes

### 1.1 Window glass seen as glass only by the camera (`materials.py`)

`window_glass_material`: Mix Shader with factor = Light Path `Is Camera Ray`: Glass BSDF (IOR 1.45,
roughness 0) for camera rays, Transparent BSDF for every other ray. The current shader over-counts the
sun 2.4× and under-counts the sky (main cause of the orange cast). Depth and object-index passes still stop
at the pane (verified: index 7, depth = pane distance). Shower panels keep the thin glass of Milestone 4.

### 1.2 Albedo modes (`vocabulary.py`, `materials.py`)

Every entry of `vocabulary.MATERIALS` gets `albedo_mode: "flat" | "texture"` and, for flat, `detail`.
- flat (colour from the vocabulary, the texture only adds luminance detail): plaster_white 0.35,
  plaster_cream 0.35, plaster_charcoal 0.35, plaster_exterior 0.5, painted_wood_white 0.5,
  painted_metal_white 0.15. Node graph (names verified in 5.2.2): TexImage (sRGB) → RGBToBW → Math DIVIDE
  by the texture's mean luminance → Math MULTIPLY_ADD (x·detail + 1 − detail) → VectorMath SCALE of the
  flat colour → VectorMath MINIMUM (0.9, 0.9, 0.9) → Base Color. Normal and roughness maps unchanged.
- texture (wood, parquet, terracotta, marble, tiles, brick, carpet, concrete): keep the texture colour with
  the mean-luminance gain, clamped to 0.5..2.5 (was 0.5..4.0), plus the 0.9 cap; `gain_clamped` recorded.
- `WALL_TINTS` entries for plaster slugs are removed (the flat colour is the colour; charcoal was darkened
  twice: albedo 0.027 instead of 0.05). The default profile's `walls.tint` goes away with it: update
  `wenart/defaults.yaml`, `tests/fixtures/style_synthetic-01.json`, `tests/fixtures/blender_style.json`.
- Material records in `scene_manifest.json` gain `albedo_mode`, `detail`, `gain_clamped`.

### 1.3 Light portals (`lighting.py`)

One AREA light per window opening, shape RECTANGLE, `size = width − 2·frame`, `size_y = height − 2·frame`,
centred in the opening, local −Z pointing into the room, `light.cycles.is_portal = True`, manifest
`kind: light, status: assumed, reason: portal`. Only valid with §1.1 (with the old glass a portal biased the
result by 23–69 %). No fill light is added to rooms with windows (exposure makes dark rooms readable;
documents say nothing about lamps).

### 1.4 Per-camera auto exposure and white balance (`render.py`)

Before each final render: a metering pre-render at 1/8 resolution, 16 samples, no denoiser, no adaptive
sampling, with the Diffuse Direct / Diffuse Indirect / Diffuse Color passes on (off again afterwards, so
the main EXR stays lean), written to a temporary EXR and read back with Blender's OpenImageIO (Render
Result pixels are not readable in background mode).
- Mask: drop window pixels (object index of any `wenart_kind == "window"` object), depth ≥ 1e9, diffuse
  albedo luminance < 0.02.
- Incident light Y = luminance(direct + indirect), averaged in blocks of `width // 40` px; Y50 = median
  of blocks with ≥ 75 % masked coverage.
- `view_settings.exposure = clamp(log2(target / Y50), lo, hi)` rounded to 1/6 stop; defaults target 0.9,
  lo −2, hi +8 (calibrated on the pod, CLI flags `--exposure auto|off|<EV>`, `--exposure-target`).
- White balance: illuminant = sum of direct + indirect over the mask, normalised to G = 1; whitepoint =
  illuminant^(1 − residual) normalised to luminance 1; residual per mood: warm daylight 0.35, golden
  evening 0.5, cool daylight 0.0, overcast 0.0, night 0.5. `view_settings.use_white_balance = True`,
  `white_balance_whitepoint = whitepoint` (Blender derives temperature and tint; both recorded).
  `--white-balance auto|off`. The mood comes from a scene property `wenart_mood` written by the build.
- View transform AgX, look None (unchanged). Exposure and white balance change the PNG/JPEG only; the
  multilayer EXR stays scene-linear (verified). Polish and gate therefore use the PNG.
- Manifest entry gains `exposure: {ev, ev_raw, at_limit, target, incident_p50, whitepoint,
  wb_temperature, wb_tint, residual, window_clip_frac, meter_seconds}` (`window_clip_frac` = fraction of
  window pixels whose display value is ≥ 0.98 in all channels, to report blown windows).

### 1.5 Helper passes, index statistics, reuse key (`render.py`)

Per camera, written while OIIO is at hand:
- `<cam>_index.png` is now **uint16** (the uint8 clip at 255 would merge masks on bigger projects);
- `<cam>_depth_mm.png`: uint16 metric camera depth in millimetres, 0 where nothing was hit or beyond 65.5 m;
- `<cam>_normal.png`: RGB8 world-space normal, `round((n + 1) · 127.5)`, (0,0,0) where nothing was hit;
- `<cam>_depth.png` stays as before (per-view normalised, near = dark) for older readers.
Manifest entry gains `index_stats: {"<index>": {"pixels": n, "box": [x0, y0, x1, y1]}}` (x1/y1
exclusive), `files: {"depth_mm": ..., "normal": ...}` and `render_key`: sha256 (first 16 hex) of the JSON
of `{samples, resolution, denoiser, exposure mode/target/limits, white balance mode, passes, hidden,
plugged, RENDER_CODE_VERSION}`. `reuse_reason` also requires an equal `render_key`; entries without one are
stale. `RENDER_CODE_VERSION = "m5.1"` (bump when the render code changes what a pixel means).

### 1.6 `--hide` and `--plug` (`render.py`, `cli.py`)

`--hide ID[,ID]`: every object with `pass_index > 0` whose `wenart_id` (without `proxy:`) is in the list
gets `hide_render = True` (door frame + leaf, window frame + glass, a furniture piece with its decor).
An id that matches nothing prints `unknown id` and exits 2. `--plug`: for hidden doors/windows, close the
baked-in wall hole with a box: wall from the opening's manifest `wall_id`, extent from the hidden objects'
world vertices projected on the wall axis, thickness = wall thickness + 4 mm, the wall object's first
material, pass index 0. Default in the controls: windows plugged, doors not (an empty doorway is not a
door). Top level and every entry of the manifest record `hidden` and `plugged`. `cli.render(..., hide=,
plug=)` passes them through. Controls render into their own folder (`outputs/<p>/controls/hide_<id>/`).

### 1.7 Build fingerprint (`build.py`, `cli.py`)

`scene_manifest.json` gains `build_fingerprint`: sha256 of the building file bytes, the style file bytes,
the assets manifest bytes (or "none"), the sorted file hashes of `wenart/blender/*.py`,
`wenart/style/vocabulary.py`, `wenart/furniture/catalog.json`, and the build arguments. `cli.build(...,
reuse=True)` skips Blender when `scene.blend` and `scene_manifest.json` exist and the fingerprint matches
(prints `BUILD_REUSED <fingerprint>`), so polish-only re-runs do not rebuild and re-render. The build also
writes `scene["wenart_mood"]` and `preview_maps: {<level>: {png, bbox_m: [x0, y0, x1, y1], m_per_px,
resolution: [w, h]}}` (the existing `previews` key stays unchanged).

## 2. AI polish (`wenart/polish`)

### 2.1 Models (all Apache-2.0, pinned)

| Role | Repo @ revision | Files | Size |
|---|---|---|---|
| base | `Tongyi-MAI/Z-Image-Turbo@f332072aa78be7aecdf3ee76d5c247082da564a6` | `model_index.json`, `scheduler/*`, `text_encoder/*` (Qwen3-4B), `tokenizer/*`, `transformer/*` (FP32 on disk, load bf16), `vae/*` (FLUX.1 VAE) | 32.85 GB |
| control | `alibaba-pai/Z-Image-Turbo-Fun-Controlnet-Union-2.1@5155fc56d17821007d6f62ac192c09e0f0e72016` | `Z-Image-Turbo-Fun-Controlnet-Union-2.1-2602-8steps.safetensors` (Canny, Depth, Pose, MLSD, HED, Scribble, Gray) | 6.71 GB |

Load: `ZImageControlNetModel.from_single_file(path, config="hlky/Z-Image-Turbo-Fun-Controlnet-Union-2.1",
dtype=torch.bfloat16)`; `ZImageControlNetPipeline.from_pretrained(repo, revision=..., controlnet=cn,
dtype=torch.bfloat16)`; `pipe.enable_model_cpu_offload()`; `pipe.vae.enable_tiling()` above 1.5 MP. The
`-2.0` id redirects to `-2.1`; use `-2.1`. `polish.yaml` holds ids, revisions, files and config ids.

### 2.2 img2img with one control image

No diffusers pipeline takes both `strength` and `control_image`, so the polish reproduces
`ZImageImg2ImgPipeline`'s maths outside and passes public arguments:
- `full = get_default_z_image_sigmas(steps)` (steps 8), `t_start = int(max(steps − min(steps·strength,
  steps), 0))`, `tail = full[t_start:]` (empty → error); `scheduler.set_timesteps(sigmas=tail)`; σ0 =
  `scheduler.sigmas[0]` (shift 3: strength 0.125 → 1 step from σ 0.30, 0.25 → 2 from 0.50, 0.375 → 3 from
  0.643, 0.5 → 4 from 0.75);
- latents: VAE encode of the render (`retrieve_latents(..., sample_mode="argmax")`), `(x − shift_factor) ·
  scaling_factor`, then `σ0 · noise + (1 − σ0) · x0` with a CPU generator seeded per attempt;
- call `pipe(prompt=..., control_image=..., controlnet_conditioning_scale=s, height=H, width=W,
  sigmas=tail, num_inference_steps=len(tail), latents=latents, guidance_scale=0.0, generator=g)`;
  H and W always explicit (the pipeline defaults to 1024×1024 and stretches the control image otherwise).
- `mode: anchor` (sweep only): `ZImageControlNetInpaintPipeline.from_pipe(pipe)` with `image=render`,
  `mask_image` all black (keep everything) and the same tail/latents: a soft colour/layout anchor.
- Prompt embeddings are computed once per prompt (`pipe.encode_prompt(..., do_classifier_free_guidance=
  False)`) and reused across attempts.

### 2.3 Size

`size: native` reflect-pads 1920×1080 by 4 px top and bottom to 1920×1088 and crops back; `size: WxH`
(both multiples of 16, e.g. 1536x864) resizes with Lanczos and back. The gate always compares at the
render size. Default `native`; the sweep measures `1536x864` too (the 2.1 ControlNets were trained on
512–1536 px control images).

### 2.4 Control images (`controls.py`, pure numpy/PIL, CPU-tested)

- `depth`: from `<cam>_depth_mm.png` (VideoX-Fun convention: near = bright): valid = depth > 0; vmin =
  p2, vmax = p85 of valid depths; x = 1 − clip((d − vmin) / (vmax − vmin), 0, 1); invalid → 0; uint8 RGB.
- `canny`: `cv2.Canny(gray(render), 100, 200)` white on black (VideoX-Fun default), RGB.
- `geometry`: white 1-px lines on black where the uint16 index changes, where the depth jumps by more than
  3 % relative, or where the normal turns by more than 30°; dilated to 2 px; RGB. No texture edges.
All controls are written as `<cam>_control_<type>.png` once per view and padded/resized like the render.

### 2.5 Prompt (`prompt.py`)

English, one paragraph, no negative prompt (guidance 0): `"Photorealistic interior photograph of a
{room_type_words} in {family} style. {wall words} walls, {floor words} floor{, furniture list}. {mood}
light through the windows, soft natural shadows, realistic materials and textures, sharp focus, 24 mm
lens."` Words come from `style.json` (material slugs → words table in `prompt.py`), the room type from the
building JSON, the furniture list from the view's expected elements (types of required and optional
furniture, deduplicated, at most 8). The prompt is recorded per view.

### 2.6 Attempt ladder and decisions

`polish.yaml: ladder` is an ordered list of attempts `{strength, control, scale, size, mode}`; default
before calibration: `[0.375 depth 0.8, 0.25 depth 0.8, 0.125 depth 0.8]` (native, plain). Per view the
attempts run in order; each attempt is gated (§3) immediately; the first accepted attempt is the view's
polished candidate; no accepted attempt → the view stays Cycles (`final: cycles`, reason `gate`). Seed =
`polish.yaml: seed` (0) + attempt number. Brief `polish: false` → every view `final: cycles`, reason
`brief`. The gate models live in the same process and are moved to the GPU only while gating.

`python -m wenart.polish run --project-out outputs/<p> [--views all|cam,...] [--config wenart/polish/polish.yaml]
[--thresholds wenart/gate/thresholds.yaml] [--force]`: writes `outputs/<p>/polish/`:
`<cam>_a<k>.png` (attempt k, render size), `<cam>_control_<type>.png`, `<cam>_a<k>_preview.jpg`
(≤ 300 KB), `polish_manifest.json` (rewritten after every attempt; resumable: an attempt is reused when its
PNG exists and its `attempt_key` (sha of settings + source PNG sha256 + model revisions) matches) and
`polish_report.md`.

`python -m wenart.polish sweep --project-out outputs/<p> --views cam,... --grid <yaml key or file>`: every
grid combination on every listed view, each gated, no early stop; writes `polish/sweep/` with the same
manifest shape (`kind: sweep`). The sweep grid: strength {0.125, 0.25, 0.375, 0.5} × control {depth,
canny, geometry} × scale {0.8} × size {native}, plus {0.25, 0.375} × depth × {1536x864} and {0.25,
0.375} × depth × mode anchor. Calibration views: 8 per project, deterministic (`sweep_views`: the views
with the most required elements, one per room, ties by camera name).

`polish_manifest.json`:
```json
{"schema_version": "0.1", "kind": "run|sweep", "project": "synthetic-01",
 "models": {"base": {"repo": "...", "revision": "...", "files": "..."}, "controlnet": {...}},
 "config": {...polish.yaml as used...}, "thresholds": {...thresholds.yaml as used...},
 "device": "cuda:0 NVIDIA ...", "torch": "2.9.1+cu128", "diffusers": "0.40.0",
 "views": [{"camera": "cam_r_L0_salon_1", "room_id": "r_L0_salon", "source_png": "../renders/cam_..png",
            "source_sha256": "...", "prompt": "...", "controls": {"depth": "cam_.._control_depth.png"},
            "attempts": [{"k": 1, "strength": 0.375, "control": "depth", "scale": 0.8, "size": "native",
                          "mode": "plain", "seed": 1, "steps": 8, "sigmas": [...], "seconds": 6.1,
                          "png": "cam_.._a1.png", "sha256": "...", "attempt_key": "...",
                          "gate": {"decision": "accept|reject", "reasons": [...], "metrics": {...}}}],
            "final": "polished|cycles", "final_attempt": 1, "reason": null}],
 "warnings": []}
```

## 3. Change gate (`wenart/gate`)

### 3.1 Inputs and regions

Reference = the Cycles PNG (display-referred), test = the polished PNG, both at render size; plus the view's
uint16 index, depth_mm and normal PNGs. Regions:
- objects: every index value > 0 (doors, windows, furniture; decor shares its host's index; plants own one);
- structure: index-0 pixels split by world normal z: floor (nz > 0.9), ceiling (nz < −0.9), walls
  (|nz| < 0.3); background (depth_mm = 0) is excluded everywhere;
- window panes: the interior of each window's index mask eroded by 6 px (the outside view) is excluded from
  edge, depth and colour metrics; the window boundary (frame) stays.

### 3.2 Metrics (`edges.py`, `depth.py`, `masks.py`, `colour.py`, `features.py`)

| Check | Metric | Starting threshold | Hard |
|---|---|---|---|
| edges | reference = index boundaries ∪ depth jumps > 3 % ∪ normal turns > 30°, kept where Canny on the reference (gray → Gaussian σ 1.5 → Canny 25/75, L2) finds an edge within 3 px; recall = share of reference pixels with a test Canny edge within 3 px (`distanceTransform`) | global ≥ 0.95; per object with ≥ 200 reference px ≥ 0.85 | yes |
| depth | DAv2-Small relative disparity on both images; test fitted to reference by least squares (scale + shift, 3 trimmed refits keeping 90 %) on non-window, non-background pixels; error = mean abs diff / (p98 − p2 of reference) | global ≤ 0.02; per object/structure region ≥ 1 % of the image ≤ 0.05 | yes |
| masks | SAM 2.1 (hiera-large) with each object's index-mask box on both images; IoU(SAM ref, SAM test); objects with IoU(SAM ref, index mask) < 0.7 are `sam_unreliable` and skipped | per object ≥ 0.5 % of the image: IoU ≥ 0.90 | yes |
| colour | CIELAB (D65, sRGB) mean per region; ΔE76 between reference and test | per object/structure region ≥ 1 %: ≤ 15; global mean ≤ 10 | yes |
| features | DINOv2-base patch tokens (518×924 grid, no centre crop), cosine per patch, mean over patches ≥ 50 % inside the object | per object ≥ 1 %: ≥ 0.80 | no (logged) |

`wenart/gate/thresholds.yaml` holds every number above with `hard: true|false` per check and a
`calibration` block (source run, date, separability per metric). Decision: `accept` iff every hard check
passes; `reasons` lists every failed check with region id and value. Metrics JSON per comparison:
`{"edges": {"global_recall", "objects": {"<wid>": recall}}, "depth": {...}, "masks": {...}, "colour": {...},
"features": {...}, "regions": {"<wid>": {"kind", "pixels"}}, "seconds": {...}}`.

The pure parts (region split, edge maps, recall, scale/shift fit, depth error, Lab/ΔE, IoU, decision) are
numpy/OpenCV and CPU-tested with synthetic arrays; the model parts (DAv2, SAM, DINOv2) are thin wrappers
with lazy `torch`/`transformers` imports and a `Models` object that can be faked in tests.

### 3.3 Calibration (`calibrate.py`, `controls.py`)

- Benign controls (must be accepted), made on the CPU from the Cycles PNG: exposure ±0.3 EV (in linear
  light), white balance (×1.05, ×1, ×0.95), Gaussian blur σ 1, JPEG quality 75, unsharp mask, Gaussian noise
  σ 3/255.
- Negative controls (must be rejected): CPU: the largest required object shifted by 25 px (pixels cut by
  its index mask, pasted, hole filled with `cv2.inpaint` TELEA), the same object erased (inpaint), scaled
  ×1.15 about its box centre; GPU: the `--hide` renders of §4.4 (real geometry removal) compared with the
  view's normal render.
- Presumed-bad (reported only): polish at strength 0.75 with control scale 0.
- `python -m wenart.gate calibrate --project-out outputs/<p> [...]` computes all control metrics and writes
  `gate/gate_calibration.json` + `gate/gate_calibration.md`: per metric the worst benign value, the best
  negative value, whether they separate, and a proposed threshold midway (rounded); the acceptance rate of
  benign (target 100 %) and the rejection rate of negatives (target ≥ 90 %) under the current thresholds.
  The proposal is applied to `thresholds.yaml` by hand after review (never automatically).

## 4. Final vision check (`wenart/vision_check`)

### 4.1 Expected elements per view (`expected.py`)

From `render_manifest.json` (`index_stats`) + `scene_manifest.json` (objects, cameras, pass_index), for
every index v > 0 of the view: `wenart_id` (pass-index inverse, `proxy:` stripped), the first manifest
object with that pass index (host before decor), `kind` (door, window, furniture, decor = plants only),
`type`, `own_room` (room_id is None or the camera's room), `pixels`, `area_frac`, `box_px`, `box_1000`,
`touches_border`, `visibility` (furniture/decor: projected oriented 3D box hull with the verified pinhole
formula: in-frame share × min(1, pixels / in-frame hull area)), `role`:
- `ignore`: area_frac < 0.002;
- `required`: kind in {door, window, furniture}, own_room, and (area_frac ≥ 0.03 or (area_frac ≥ 0.01 and
  (visibility is None or visibility ≥ 0.35)));
- `optional`: everything else (decor and other-room elements are never required).
Thresholds in `wenart/vision_check/check.yaml`. Each element carries its building-JSON evidence (file,
page, entity) so every verdict traces back to the source plan. Output `check/expected_views.json`.

### 4.2 Prompt, schema, request

One call per (image, model). Labels E1..En by descending area for required + optional elements, plus one
sentinel decoy label shuffled in deterministically (sha1 of camera): type = first allowed type of the room
type that the room does not contain (fallback list armchair, desk, bookshelf, bathtub), box = a 0.18W ×
0.25H window over bare structure (index 0, ≥ 98 %), searched in 5 % steps, lowest-centre tie-break. Each
line: `- E3: tv_unit (low long cabinet / sideboard); expected inside box [83, 674, 362, 933][, cut by the
image edge]`. The prompt defines the statuses, says an empty doorway without a door leaf is NOT a door, and
excludes walls, floor, ceiling, lamps, curtains and the outside view from extras.

Per-view strict schema (verified to compile in xgrammar 0.2.1): `{"elements": {E1: ELEM, ...}
(all required, additionalProperties false), "extras": [≤ 8 {category, box (0..1000), confidence}],
"door_count": int 0..20, "window_count": int 0..20}`, ELEM = `{status: present|different|absent|unsure,
seen_as: CATEGORIES + nothing, confidence 0..1}`, CATEGORIES = door, window, the building furniture types
(without unknown), plant, cushion, book_set, other_furniture, other_object (generated from the schema
enums so they cannot drift). Request as `vlm_client.build_request` (temperature 0, seed 0, structured
outputs, thinking off) but with a dynamic schema and content parts; post-validation normalises
inconsistent answers to `unsure` (present but seen_as another category; absent but seen_as not nothing;
different but seen_as the listed type).

### 4.3 Two models and verdicts (`combine.py`)

Pass 1 Qwen3-VL-8B-Instruct, pass 2 GLM-4.6V-Flash, independent, one server at a time (as `bakeoff.sh`:
port 8001, fp8 and 8192 context below 40 GB, `--limit-mm-per-prompt '{"image":2}'`, GLM with
`--reasoning-parser glm45`, `VLLM_USE_FLASHINFER_SAMPLER=0`). Per element (A, B): present+present → ok;
absent+absent → missing; different+different → changed; absent+different → missing_or_changed; present vs
absent/different → disputed; any unsure → the other pass's result, `unverified`; a failed call →
`not_computed` (never absent); a pass that answers the decoy present → that pass is `unreliable` for the
view (its verdicts become unsure). Extras: drop those whose box is ≥ 50 % covered by any indexed mask;
match A and B extras by IoU ≥ 0.3 and the same class (door/window/furniture/decor) → confirmed; decor
extras are info only. Counts: expected range [required, required + optional + ignored]; a mismatch needs
both models outside the range on the same side. Only required elements and confirmed non-decor extras make
a view `mismatch`; everything else is `info`. Nothing is auto-fixed.

### 4.4 Calibration and controls (`calibrate.py`)

- Baseline: every Cycles view, both models. FA_missing = required elements not judged present / required;
  FA_extra = views with a confirmed non-decor extra / views; count error rate; decoy acceptance per model.
- Removal controls: per project up to 3 furniture, 3 windows, 2 doors from required own-room elements with
  area_frac ≥ 0.03 not touching the border, one per room and per id, largest first
  (`python -m wenart.vision_check select-controls`); each re-rendered with `--hide` (windows `--plug`) for
  its camera; the expected list stays the original one, so the element must come back absent or different.
  Sanity: the control's index stats must not contain the element's index, else the control is dropped.
- Insertion controls (free): image = the normal render, expected list recomputed from the hidden render;
  the checker must report an extra covering ≥ 50 % of the element's original box.
- Targets (defaults, `check.yaml`): combined FA_missing ≤ 5 %, FA_extra ≤ 10 % of views, removal detection
  ≥ 80 % flagged by at least one model and ≥ 60 % confirmed, insertion detection ≥ 60 %, decoy acceptance
  ≤ 10 % per model. When a target is missed, the report marks the check `advisory` for this run (it still
  lists every finding but no longer rejects polish).
- Plan image A/B (`--plan-image`): a second image, the room crop of the level top view with the camera and
  its view cone drawn, interleaved as "Image 2 (top-down plan of the room, for orientation)". Run on the
  calibration set only; adopted only if removal detection rises and false alarms do not.

### 4.5 Use in the decision and the realism preference

Every view is checked twice: its Cycles render and its polished candidate (when there is one). A polished
candidate with a confirmed missing/changed required element or a confirmed extra that its Cycles render
does not have is rejected → `final: cycles`, reason `vision_check` (only when the check is not advisory).
Pairwise realism preference (`preference.py`, info only): both models, both orders (A/B and B/A), "Which
image looks more like a real photograph of a room?" with schema `{"choice": "first|second|same",
"confidence"}`; a polished image is `preferred` when at least 3 of the 4 answers pick it. Used to compare
sweep settings among gate-accepted attempts and reported per view.

CLI: `python -m wenart.vision_check expected|select-controls|run|combine|calibrate|preference ...` with
`main(argv=None, client_factory=None)`; outputs in `outputs/<p>/check/`: `expected_views.json`,
`answers_<model-slug>.json` (every call: image kind, prompt, raw text, parsed data, latency, error;
rewritten after every call, resumable by `call_key`), `check_manifest.json` (verdicts per view and image
kind), `check_calibration.json`, `check_report.md`.

## 5. Style reference photos (`wenart/style/photos.py`, `wenart/brief.py`)

- `wenart/brief.py`: `load_brief(project_dir) -> dict` reads `projects/<p>/brief.yaml` with the defaults
  of `wenart/defaults.yaml` (`polish: true`, `style_photos: []` added to the `brief:` block) and returns
  `{"values": ..., "assumed": [keys filled from defaults]}`. New readers use it; existing readers stay.
- Photos live in `projects/<p>/style_photos/` (the ingest classifier only reads top-level files).
- `read_style_photo(path, client, passes=2)`: Qwen3-VL-8B, temperature 0, two passes (seed 0 and 1, field
  order swapped in the instruction), strict schema with enums from the vocabulary: floor (8 slugs), walls (5
  slugs), light mood (5), family (9), each plus `unclear`. Values both passes agree on (and not unclear)
  become style terms with evidence `{method: ai, model, pass, file}`.
- `profile_from_brief(brief, photo_terms=...)`: photo terms fill only slots the brief text does not name
  (slots that would otherwise be `assumed` from the family word or the defaults); the brief always wins;
  every use is listed in `matched_terms` as `photo:<file>:<term>` and in the warnings.
- CLI: `python -m wenart.style projects/<p> --out ... [--photos-server URL --photos-model ID]`; without a
  server the photos are listed as `not read` in the warnings.
- GPU test: the committed render `results/renders/synthetic-03/cam_r_L0_salon_1_preview.jpg` (our own
  image, charcoal walls, polished concrete floor) is read as a style photo; expected walls
  plaster_charcoal and floor concrete_polished (both passes agree).

## 6. Final report (`wenart/report`)

`python -m wenart.report final --project-out outputs/<p>` writes `outputs/<p>/final/`:
`final_manifest.json` (per view: camera, room, final image path, `polished|cycles`, reason, the chosen
attempt's settings and gate summary, vision-check verdicts for both images, preference, exposure),
`<cam>_final_preview.jpg` (≤ 300 KB), `contact_<level>.jpg` (grid of the level's final views, 480 px wide
tiles, label with camera and `P`/`C`, ≤ 300 KB, quality steps down until it fits) and `final_report.md`:
summary table (views, polished, Cycles by reason, mismatches, advisory flags, exposure range, seconds per
stage), per-view table, every mismatch and disputed element (never auto-fixed), the `unverified` items and
conflicts carried from `building.json`, and the model/licence table of everything used.

## 7. Pod job and setup

`scripts/pod_setup_polish.sh` (idempotent, timed, logged, container disk): `/opt/wenart/venv-polish`
(`--system-site-packages`, image torch 2.9.1): `diffusers==0.40.0 transformers==5.18.0 accelerate==1.15.0
huggingface-hub==1.33.0 safetensors>=0.8.0 opencv-python-headless==4.14.0.94` + the repo's CPU deps
(`pod_requirements.txt` without its hub pin); stamped good only after a CUDA matmul and the imports of
`ZImageControlNetPipeline`, `Sam2Model`, `AutoModelForDepthEstimation`. Downloads into `HF_HOME=/opt/wenart/hf`
with pinned revisions: Z-Image-Turbo (allow patterns as §2.1), the ControlNet file,
`depth-anything/Depth-Anything-V2-Small-hf`, `facebook/sam2.1-hiera-large`, `facebook/dinov2-base` (the
implementation pins their current revisions from the HF API). Records sizes, seconds, free disk and RAM in
`$WENART_RESULTS/setup_polish.json`. The vLLM part reuses `scripts/pod_setup_recognition.sh` with only the
vLLM venv and the two VLM checkpoints (new switch `RECOG_SETUP_PARTS="vllm models"` skips PaddleOCR and
LibreDWG).

`scripts/jobs/polish.sh` (same skeleton as `furnish.sh`: `set -Eeuo pipefail`, error trap, timed
`run_stage`, `copy_results` after every stage and from the EXIT trap, exit 1 when a stage failed). Env:
`POLISH_PROJECTS` (default `synthetic-01 synthetic-03`), `POLISH_MODE` (`sweep` | `final`, default `final`),
`POLISH_PHASES` (default `look controls polish gate check report tests`), `RENDER_SAMPLES` (128),
`FORCE_RENDER`, `FORCE_POLISH`, `CHECK_MODELS` (default both).
- `look`: inputs `outputs/<p>/building_final.json` and `style.json` on the volume, else the committed
  `results/furniture/<p>/building_final.json` and a fresh `python -m wenart.style`; assets fetch; build
  (`reuse`); render all cameras (auto exposure, white balance).
- `controls`: `select-controls`, then one `render --hide [--plug] --cameras <cam>` per control.
- `polish`: `run` (final) or `sweep` (sweep views), gate inline.
- `gate`: `gate calibrate`.
- `check`: Qwen server up → `vision_check run` for all image kinds (+ `preference`) → down → GLM up → same →
  down → `combine` → `calibrate`.
- `report`: `report final`. `tests`: `pytest -m gpu tests/gpu/test_render.py tests/gpu/test_polish.py
  tests/gpu/test_check.py` with junit files in the results.
`copy_results`: JSON/MD of every stage, render/polish/final previews (`*_preview.jpg` ≤ 300 KB), contact
sheets, gate and check reports, logs (tails), junit. Run with `scripts/gpu_run.py run --job
scripts/jobs/polish.sh --disk 130 --env POLISH_MODE=...`.

Pod plan: run 1 `POLISH_MODE=sweep` (look, controls, sweep, gate calibration, check calibration);
thresholds, ladder and check roles are then set from its numbers here in the session (committed with the
numbers); run 2 `POLISH_MODE=final` (look reused by fingerprint, polish ladder on every view, check,
report, GPU tests). Expected ≈ 60–80 min per run (≈ $0.6), inside the 2 h cap.

## 8. Tests

CPU (`pytest -m "not gpu"`):
- Blender (skip without Blender): camera-only glass node graph and index/depth at the pane; flat albedo graph
  output (white plaster albedo within 0.03 of the flat colour, CV < 0.06 on a tiny render); portals count,
  size, orientation (−Z into the room); metering on a tiny room returns finite EV within the clamp and a
  whitepoint; `render_key` reuse/re-render; uint16 index PNG round trip; `depth_mm` and `normal` PNGs
  agree with the EXR; `--hide`/`--plug` (index gone, depth at the wall, unknown id → exit 2); build
  fingerprint reuse.
- polish: sigma tail and σ0 for the grid strengths, pad/crop and resize round trips, control images
  (depth convention, canny, geometry edges), prompt words, ladder and resumability with a fake pipeline and
  a fake gate, manifest schema, `polish: false`.
- gate: region split, reference edges and recall (shift of 25 px must fail, texture noise must pass),
  scale/shift fit and depth error, Lab/ΔE, IoU, decision, every benign and negative control generator,
  calibration proposal on synthetic metrics, faked models.
- vision_check: expected elements and roles from a hand-made manifest + index array, projection against a
  known camera, decoy placement, schema strictness (missing/extra labels, bad enums), post-validation,
  combine table (every row of §4.3), extras matching, counts, calibration metrics, preference rule, fake
  client end to end, resumable answers.
- style photos with a fake client (agreement, unclear, brief wins), `brief.py` defaults.
- report from hand-made manifests; contact sheet size limit.
- job scripts: `bash -n`, required stages and flags (regex), `--disk 130` documented.
GPU (`pytest -m gpu` on the pod): `tests/gpu/test_render.py` stays green (now also: exposure recorded and
within the clamp, uint16 index stats consistent with `index_values`, white plaster walls of synthetic-01
display-referred mean within 10 % of neutral grey balance R/B ≤ 1.10); `tests/gpu/test_polish.py` (every
view has a final image of render size; every accepted attempt passes every hard threshold recomputed from
its stored metrics; rejected attempts have reasons; sweep/final manifests valid; benign controls accepted
100 %, negatives rejected ≥ 90 % or the gate report says why; determinism: one view polished twice gives a
max abs pixel difference ≤ 2); `tests/gpu/test_check.py` (≥ 95 % of calls answered by each model;
calibration metrics present; `advisory` set exactly when a target is missed; the style photo test of §5).

## 9. Done criteria

`pytest -m "not gpu"` green here; run 1 and run 2 green on the pod; thresholds and ladder set from run 1's
numbers and committed with them; previews, contact sheets, manifests and reports committed under
`results/renders/<p>/`, `results/polish/<p>/`, `results/check/<p>/`, `results/final/<p>/`;
`docs/plan.md` §4.12–4.13 updated to §0; `docs/progress.md` and `docs/gpu-log.md` updated; every pod
stopped.

## 10. Sources (checked 2 Oct 2026)

- diffusers 0.40.0 wheel: `pipelines/z_image/pipeline_z_image_controlnet.py` (sigmas/latents arguments,
  control encoding, 1024 default), `pipeline_z_image_img2img.py` (get_timesteps, prepare_latents),
  `pipeline_z_image_controlnet_inpaint.py` (mask semantics), `models/controlnets/controlnet_z_image.py`;
  METADATA (torch ≥ 2.6, huggingface-hub ≥ 1.23, < 2.0).
- Hugging Face API and model cards: Tongyi-MAI/Z-Image-Turbo (apache-2.0, guidance 0, 8 forwards),
  alibaba-pai/Z-Image-Turbo-Fun-Controlnet-Union-2.1 (apache-2.0, control types, context scale
  0.65–1.0), depth-anything/Depth-Anything-V2-Small-hf (apache-2.0; Base/Large cc-by-nc-4.0),
  facebook/sam2.1-hiera-large (apache-2.0, transformers files in the repo), facebook/dinov2-base
  (apache-2.0), Qwen/Qwen3-VL-8B-Instruct (apache-2.0), zai-org/GLM-4.6V-Flash (MIT).
- transformers 5.18.0 (PyPI; Sam2Model since 4.56.0), VideoX-Fun `comfyui/annotator/nodes.py` (depth and
  canny control conventions), vLLM v0.30.0 docs (multi-image, `--limit-mm-per-prompt`).
- Blender 5.2.2 (local probes): view transforms and looks, `ColorManagedViewSettings` white balance
  properties, `light.cycles.is_portal`, Render Result unreadable in background mode, EXR unaffected by view
  settings, shader node and socket names.
