# Milestone 8 – better furniture (product-quality library, generated models, real decor) and wider lenses

Goal: the furniture in the renders looks like real products in the project's style, not like grey boxes or random
web models, and the cameras show more of each room. User decisions of 4 Oct 2026 (after Milestone 7):

| # | Item | Decision |
|---|---|---|
| 1 | real01 style | the user adds `projects/real01/brief.yaml` later; nothing to do now |
| 2 | AI polish | decide from the cost (≈ $0.02 per view, ≈ $0.40 for real01; `docs/progress.md`) |
| 3, 4 | Furniture | "we need better furniture, this is a must; do whatever is needed"; licences may be ignored for now |
| 5 | Warm white walls with AgX Punchy | accepted |
| 6 | Cameras | use wider lenses |

The furniture and no-hallucination rules of `CLAUDE.md` stay: a drawn piece keeps its type, position, orientation and
footprint; only its look changes. Licences are recorded for every model (and flagged when not CC0 / CC BY), even
though the user allows any licence for now.

Research (4 Oct 2026, from the session):
- **Amazon Berkeley Objects (ABO)**, `https://amazon-berkeley-objects.s3.amazonaws.com/` (reachable from the session
  and the pods): 7,953 glTF models of real products with PBR textures (2k–4k) and real sizes in metres
  (`3dmodels/metadata/3dmodels.csv.gz`: `3dmodel_id, path, meshes, materials, textures, images, …, vertices,
  faces, extent_x, extent_y, extent_z`; the GLB is `3dmodels/original/<path>`). Licence **CC BY 4.0**, credit
  "Amazon.com" for the data and "Matthieu Guillaumin, Thomas Dideriksen, Kenan Deng, Himanshu Arora (Amazon.com),
  Jasmine Collins and Jitendra Malik (UC Berkeley)" for the dataset (`3dmodels/README.md`). The listings
  (`listings/metadata/listings_{0..9,a..f}.json.gz`, one JSON object per line) give `3dmodel_id`, `product_type`,
  `item_name` (many languages), `style`, `color`, `material`, `item_dimensions`, `brand`. Listings with a 3D model,
  by product type: CHAIR 1184, SOFA 859, RUG 817, WALL_ART 599, TABLE 584, HOME_FURNITURE_AND_DECOR 550,
  LAMP 345, STOOL_SEATING 340, OTTOMAN 288, PILLOW 275, HEADBOARD 206, LIGHT_FIXTURE 197, PLANTER 182, DESK 145,
  BED 140, CABINET 137, HOME_MIRROR 109, SHELF 106, DRESSER 62, BED_FRAME 52, VASE 50, BENCH 39, … No sanitary
  ware, no kitchen appliances. English styles seen: modern 551, transitional 479, contemporary 416, mid-century
  modern 178, industrial 118, rustic 99, classic 86, traditional 82, farmhouse 31, bohemian 31, glam 23, …
- **TRELLIS.2-4B** (`microsoft/TRELLIS.2-4B` @ `af44b45f2e35a493886929c6d786e563ec68364d`, MIT; code
  `github.com/microsoft/TRELLIS.2`, MIT; nvdiffrast / nvdiffrec under their own licences): image → textured 3D
  (PBR GLB). ≥ 24 GB GPU; verified by the authors on A100/H100 only; ~17 s per object at 1024³ on an H100;
  `setup.sh --basic --flash-attn --nvdiffrast --nvdiffrec --cumesh --o-voxel --flexgemm` compiles CUDA
  extensions (the RTX PRO 6000 is Blackwell, sm_120: build with `TORCH_CUDA_ARCH_LIST=12.0`; `ATTN_BACKEND` falls
  back to `xformers`/`sdpa` when flash-attn does not build). Input images come from Z-Image-Turbo, which the pod
  already has for the polish (`Tongyi-MAI/Z-Image-Turbo`).
- Objaverse 1.0 is already surveyed (M7); this milestone drops the licence filter (any licence, flagged).

## 1. Sources and order of preference

| Order | Source | Licence | Types | Where |
|---|---|---|---|---|
| 1 | ABO | CC BY 4.0 | seating, tables, beds and frames, desks, cabinets, dressers, shelves, lamps; decor: rugs, wall art, cushions, plants | `wenart/assets/abo.py` (new) |
| 2 | Poly Haven | CC0 | as today | unchanged |
| 3 | Objaverse 1.0 | any (flagged unless CC0 / CC BY 4.0) | every type, mainly bathroom and kitchen | `wenart/assets/objaverse.py` (licence filter → flag) |
| 4 | Generated (TRELLIS.2) | MIT model; output marked `generated` | every (type, style family) still without an accepted model | `wenart/assets/generate.py` (new) |
| 5 | Parametric | ours | everything else, and fixed equipment (stairs, kitchen counters) | unchanged |

The fit takes a model only when its `styles` contain the project's style family or `neutral` (M7 rule), then
ranks by **real size** (models with known units: the smallest scale change wins), then judge quality, then aspect
error, then source order. A generated model is used only when no real model fits the style and size.

## 2. One library pipeline for every source

`wenart/assets/objaverse.py` keeps its steps; the survey step becomes per source and the later steps read every
source's survey records (field `source` ∈ `objaverse`, `abo`, `generated`). Records keep the M7 shape (`uid`,
`type`, `glb` local path, `sha256`, credit fields, `licence`, `extents_raw`, `units_known`), plus:
- `source`, `licence_flag` (`null` for CC0 / CC BY 4.0, else `non_commercial` / `share_alike` / `no_derivatives` /
  `unknown`; recorded, never filtered while the user allows it), `style_hint` (ABO `style` text or the generation
  prompt's family), `kind` (`furniture` or `decor`), `decor_type` (decor only).
- The uid of an ABO record is `abo_<3dmodel_id>`, of a generated one `gen_<type>_<family>_<n>_<sha8>`.

ABO survey (`python -m wenart.assets.abo survey --out DIR [--cache /opt/wenart/abo] [--metadata DIR]`): reads the
16 listings shards and `3dmodels.csv.gz` (cached), maps each listing with a 3D model to a type with the table in
`wenart/assets/abo.yaml` (product type + English `item_name` keywords + extents; e.g. TABLE + "coffee" →
`table_coffee`, TABLE + "nightstand"/"bedside" → `nightstand`, TABLE + "side"/"end"/"accent" → `side_table`,
TABLE + "dining" → `table_dining`, CABINET + "wardrobe"/"armoire" → `wardrobe`, CABINET + "tv"/"media" →
`tv_unit`, LAMP with extent_z ≥ 1.2 m → `floor_lamp`, BED/BED_FRAME by width → `bed_single` / `bed_double`,
SHELF with extent_z ≥ 1.0 m → `bookshelf`, CHAIR + "arm"/"accent"/"lounge"/"club" → `armchair`, else `chair`;
decor: RUG → `rug`, WALL_ART → `wall_art`, PILLOW → `cushion`, PLANTER → `plant`), deduplicates by
`3dmodel_id`, drops models with extents outside the type's size table (+ 15 %) or > 60 MB, picks **≤ 24
candidates per type** spread over the ABO style values (round robin over styles, then by texture size), and
downloads their GLBs (`3dmodels/original/<path>`, sha256 recorded). Units are metres (`units_known: true`).

Thumbnails, judging and acceptance stay as in M7 §7.2 with these changes:
- the judge also answers `has_mattress` for beds (as today) and, for decor, `is_decor_type` (a rug is a rug, a
  planter holds a plant);
- **beds without a mattress are accepted as bed frames** (`bed_frame: true`) when everything else passes: the
  thumbnail step measures the deck height (`deck_height_m`: median of 5 downward rays inside the inner 50 % of the
  footprint, in the Z-up model frame, metres) and the scene builder puts the parametric mattress, duvet and pillows
  on it (§4); a bed frame without a measurable deck is refused (`no_deck`);
- per-type limit 12 (decor 16), at most 3 per (type, style family), ranked by mean quality then source order;
- a model whose units are known is refused when its size is outside the type's range (no normalisation).

`write-catalog` writes one `catalog_library.json` (replaces `catalog_objaverse.json`; `catalog.load` merges it
the same way) with the M7 entry fields plus `source`, `licence_flag`, `quality`, `bed_frame`, `deck_height_m`,
`kind`/`decor_type`, `generated` (generated only: `{prompt, image_sha256, model, revision, seed}`); GLBs go to
`<assets>/models/<source>/<uid>.glb`. `ATTRIBUTION.md` lists every non-CC0 model with its credit line (ABO:
`"<item name>" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), https://amazon-berkeley-objects.s3.amazonaws.com/index.html`).

## 3. Generated models (TRELLIS.2)

`python -m wenart.assets.generate plan --catalog … --families F1,F2 --out DIR` lists the (type, family) pairs with
no accepted model (after ABO, Poly Haven, Objaverse) for the furniture types that are not fixed equipment
(not `stair`, `kitchen_counter`, `kitchen_island`, `unknown`), for the style families of the committed projects'
`style.json` plus the default family. `generate run --out DIR --plan plan.json` (venv-trellis, GPU) for each pair:
1. prompt (fixed template per type, `wenart/assets/generate.yaml`): "a single {family} style {type words},
   {material hints of the family}, studio product photo, three-quarter front view from the left, full object in
   frame, plain white background, soft even light, no people, no text";
2. Z-Image-Turbo text-to-image (the polish venv's diffusers pipeline; 1024 × 1024, 8 steps, seed = fixed
   per pair, 2 images per pair);
3. background removal is not needed (white background; TRELLIS.2's own preprocessing crops);
4. TRELLIS.2 `Trellis2ImageTo3DPipeline.run(image)` at its default resolution, `o_voxel.postprocess.to_glb(…,
   decimation_target=200000, texture_size=2048)`;
5. a survey record with `source: generated`, `units_known: false` (normalised by type in thumbnails, M7 rule),
   `licence: "generated (TRELLIS.2-4B, MIT)"`, `licence_flag: null`, the prompt and image hash.
The generated candidates then go through thumbnails, judging (front agreed, quality ≥ 4, type matches, styles) and
acceptance like any other model. Time budget: ≤ 2 pairs per minute; the step watches `WENART_DEADLINE`.
`scripts/pod_setup_trellis.sh` builds venv-trellis on the container disk (`/opt/wenart/venv-trellis`, torch of the
pod image, `TORCH_CUDA_ARCH_LIST=12.0`), downloads the model into `HF_HOME`, records versions in
`setup_trellis.json`; built wheels are cached on the volume (`/workspace/wheels/trellis/`) so the next pod installs
them in minutes. A failed build ends the step `failed` with the reason; the library is then built without
generated models (never silently).

## 4. Builder changes

- **Bed frames**: a library bed with `bed_frame: true` gets the parametric mattress (top at `deck_height_m` +
  0.20 m), duvet and pillows of the parametric bed, sized to the frame's inner box (the footprint minus 4 % per
  side), in the frame's coordinates; the bed's pass index covers frame and bedding (one piece).
- **Decor library**: decor items of type `cushion`, `plant`, `rug`, `wall_art` use a library decor model of the
  project's style family (or `neutral`) when the catalogue has one (deterministic pick by host id), else the
  parametric decor (cushion, plant) or none (rug, wall art).
- **New decor rules** (`wenart/furniture/decor.py`, only when the brief allows decor, default yes): a rug under the
  sofa + coffee table group (living), under the lower two thirds of a double bed (bedroom), under the dining table
  (+ 0.6 m each side for the chairs) — rug size = the group box + 0.3 m, clipped to the room shrunk by 0.3 m,
  never under a door swing; one wall art piece centred above a sofa, a bed's headboard or a sideboard/dresser on
  the wall behind it, bottom edge 0.25 m above the piece top, width ≤ 0.6 × the piece width, never over a window
  or door opening. Decor is labelled decor (`added_by_ai`, not furniture) in the building JSON and the report.

## 5. Cameras

`cameras.LENS_MM` 24 → **18 mm** (horizontal field of view 73.7° → 90°); rooms whose shorter side is < 2.2 m get
**16 mm**; the brief may set `render.lens_mm` (14–35). Every consumer reads the camera's own `lens_mm` (camera
search ray grid, expected elements, plan crops, gate, detector); render keys change, so everything re-renders.
The white-wall test limit becomes R/B ≤ 1.12 under AgX Punchy (decision 5).

## 6. Prep pods (library build)

Prep job steps (new order): `abo_survey`, `survey` (Objaverse, all licences), `trellis_setup`, `generate`
(needs the catalogue of the earlier steps: it runs after a first `accept` on the real models), `thumbnails`,
`judge_requests`, `session_qwen`, `session_glm`, `accept`, `library` (write-catalog + report), `copy`, `tests`.
Two pods: L1 = real models (ABO + Objaverse + judging + catalogue), L2 = TRELLIS.2 setup + generation + judging +
catalogue merge. Then the full runs of all projects (two pods as in M7).

## 7. Tests

CPU: ABO mapping table on canned listings (each mapping row, dedup, style round robin, size filter), survey records
(shape, uid, credit), licence flags, catalogue validation of every source, fit ranking (style → size → quality →
aspect → source), bed-frame catalogue fields and the builder's mattress placement (Blender, skip without it), decor
rules (rug and wall art geometry, never over openings, brief off → none), lens selection and every lens consumer,
generation plan (gaps only, fixed equipment excluded), prompt template. GPU: `test_library.py` (sources present,
attribution complete, bed frames have decks), `test_generate.py` (TRELLIS.2 loads, one object generated and judged),
`test_render.py` (18/16 mm, decor rugs and wall art in the index pass as decor).

## 8. Done criteria

CPU suite green; L1, L2 and the full runs exit 0; every project `ok`; the share of furniture pieces built from a
library or generated model (not parametric) reported per project and above 70 % for movable furniture; renders at
18/16 mm; results, docs (`docs/plan.md` sources and licences, `docs/progress.md`, `docs/gpu-log.md`) committed; no
pod running.
