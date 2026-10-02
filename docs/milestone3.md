# Milestone 3 – 3D shell, materials, lighting, first Cycles renders

Goal: turn a building JSON into a textured Blender scene and render every room from three cameras
with Cycles on the pod. Documented furniture appears as labelled proxy boxes at the drawn footprints
(real assets come in Milestone 4). Two recognition follow-ups from Milestone 2 ride along: the tiled
symbol pass and LibreDWG 0.14.1.

Scope:
1. Style profile from the brief (`wenart/style`), deterministic, no AI yet.
2. CC0 material and HDRI assets with licence manifest (`wenart/assets`).
3. Blender scene from the building JSON (`wenart/blender`): shell, openings, furniture proxies,
   materials, lighting, cameras, render passes, exports, manifests.
4. Pod job `scripts/jobs/render.sh`: pipeline → scene → renders of the three synthetic projects,
   GPU tests, previews.
5. Recognition: `wenart/recognition/tiles.py` (crop-to-drawing + tiles for the symbol pass) and
   LibreDWG 0.14.1 in `scripts/pod_setup_recognition.sh`.

Out of scope: real furniture assets, AI layout of empty rooms, AI polish, the final vision check.

## Conventions

- Blender 5.2 LTS, headless: `blender -b --python <script> -- <args>`. Local copy for CPU tests in
  this environment: `/opt/wenart/blender/blender` (pod: `/workspace/tools/blender/blender`). The code
  under `wenart/blender` imports `bpy` lazily and is run inside Blender; pure helpers (geometry,
  manifests, camera placement maths) must import without `bpy` so the CPU tests cover them.
- Units: metres, Z up. Building frame X right, Y up (north) → Blender X, Y, Z. Level `L<k>` floor at
  its `elevation`, ceiling at `elevation + ceiling_height`.
- Every Blender object carries custom properties `wenart_id` (element id or `proxy:<furniture id>`),
  `wenart_kind` (wall, floor, ceiling, door, window, opening, furniture_proxy, camera, light) and
  `wenart_status` (verified / unverified / assumed). Object names are the element ids
  (`w_L0_001`, `r_L0_salon_floor`, `d_L0_001_frame`, ...).
- Defaults when the JSON has `null` (recorded as `assumed` in `scene_manifest.json`): door height
  2.10 m, window sill 0.90 m, window height 1.20 m (1.40 m when the opening is wider than 1.5 m),
  plain opening full height, wall height = level ceiling height, slab thickness 0.30 m between levels.
- Furniture proxies: a box of the footprint size, height per type from `wenart/blender/proxies.py`
  (bed 0.55, sofa 0.85, armchair 0.85, table_dining 0.75, table_coffee 0.45, desk 0.75, chair 0.9,
  wardrobe 2.1, bookshelf 1.8, tv_unit 0.5, nightstand 0.5, dresser 0.8, kitchen_counter 0.9,
  kitchen_island 0.9, fridge 1.8, stove 0.9, sink_kitchen 0.9, washbasin 0.85, toilet 0.4, shower 2.0
  (glass look), bathtub 0.55, washing_machine 0.85, unknown 0.8). Rotated by `footprint.rotation_deg`,
  a small wedge on the front face shows `front_deg`. Material: neutral mid-grey, `unverified` pieces in
  a dashed-red look (emission stripes) so a reviewer sees them in the renders.
- Nothing is added, moved or removed: proxies come only from `building.furniture`; rooms without
  documented furniture stay empty in this milestone.

## 1. `wenart/style` (brief → style profile)

`profile_from_brief(brief: dict | None) -> dict` with `style.json` shape:
```json
{"source_text": "...", "floor": {"material": "wood_oak_light", "asset": "WoodFloor051"},
 "walls": {"material": "plaster_white", "asset": "Plaster001", "tint": [0.95, 0.94, 0.90]},
 "ceiling": {"material": "plaster_white"}, "wet_floor": {"material": "tiles_light", "asset": "Tiles074"},
 "wet_walls": {"material": "tiles_light"}, "trim": {"material": "painted_wood_white"},
 "door": {"material": "wood_oak_light"}, "window_frame": {"material": "painted_metal_white"},
 "lighting": {"hdri": "kloppenheim_06", "sun_elevation_deg": 35, "sun_azimuth_deg": 210,
              "sun_strength": 3.0, "colour_temperature_k": 5200, "mood": "warm daylight"},
 "matched_terms": ["Scandinavian", "light oak floor", "white walls", "warm daylight"],
 "unmatched_terms": ["linen textiles"], "warnings": []}
```
Rule-based keyword table (`wenart/style/vocabulary.py`): floor words (oak, walnut, parquet, concrete,
terracotta, marble, tiles, carpet), wall words (white, cream, charcoal, plaster, brick, wood panel),
light words (warm daylight, cool daylight, golden evening, overcast, night) → HDRI id + sun settings.
Wet rooms (`room_type` bathroom / wc / kitchen) get `wet_floor` / `wet_walls`. Unknown words are
listed, never guessed; `wenart/defaults.yaml` holds the default style text and the default profile.
Multiple styles (`brief.styles: [...]`) → `profiles_from_brief` returns one profile per entry; the
render job renders the first and notes the others.

## 2. `wenart/assets` (CC0 PBR textures and HDRIs)

- `fetch_texture(asset_id, out_dir, size="2k") -> dict` and `fetch_hdri(asset_id, out_dir, size="2k")`:
  Poly Haven API (`https://api.polyhaven.com/assets?type=textures`, `/files/{id}`; files on
  `dl.polyhaven.org`), ambientCG as the second source (`https://ambientcg.com/api/v2/full_json?id=...`,
  zip of the 2K-JPG set). Verify both APIs with real calls (both domains are reachable here) and record
  the response fields you rely on in docstrings. Downloads go to `assets/` (git-ignored; on the pod
  `/workspace/assets`, few large files → fine on the volume), with `assets/manifest.json` listing id,
  source, licence (must be CC0; anything else is refused), url, files, sha256. Idempotent.
- The style vocabulary maps material slugs to concrete asset ids that exist (check them against the APIs
  in a CPU test that only lists, no bulk download; one small texture and one 1k HDRI are downloaded in
  the test to prove the path). Fallback when offline: flat colours per material slug
  (`wenart/style/vocabulary.py: FLAT_COLOURS`) and a plain sky; the scene manifest records which
  materials are textured and which are flat.

## 3. `wenart/blender` (inside Blender)

- `build.py`: entry `blender -b --python wenart/blender/build.py -- --building outputs/<p>/building.json
  --style outputs/<p>/style.json --assets assets --out outputs/<p>/scene [--level L0] [--no-textures]`.
  Writes `scene.blend`, `scene.glb`, `scene_manifest.json` (every object: name, wenart_id, kind, status,
  element evidence copied from the JSON, material slug, textured or flat, assumed defaults), and a
  top-down preview PNG per level (`level_L0_top.png`, orthographic, 100 px/m) for the report.
- `shell.py`: walls = extruded rectangles from centre line, thickness, height (per wall, merged per
  level into one mesh with per-face material slots: interior faces get wall material, exterior faces an
  exterior plaster). Openings: boolean cut per opening (a box of width × wall thickness + 2 cm × height
  at centre; door from floor, window from sill). Door leaf and frame as simple geometry (frame 5 cm,
  leaf 4 cm thick, opened 0° = closed; closed by default), window = frame + glass pane (glass BSDF).
  Floors = room polygon faces at level elevation (one object per room, material per style/wet rule),
  ceilings = same polygon at ceiling height facing down. Rooms with `status: unverified` keep the same
  geometry; their floor material gets the dashed-red overlay.
- `proxies.py`: furniture proxies as above.
- `materials.py`: `pbr_material(slug, texture_set: dict | None, tint, scale_m)`: Principled BSDF with
  albedo / normal / roughness (and displacement off), box-projection UVs with the texture's real-world
  size (Poly Haven `dimensions`, ambientCG default 1 m) so a tile is the right size; flat fallback.
  Glass, emission-stripes (unverified) and sun/world nodes live here too.
- `lighting.py`: world HDRI from the style (strength from mood), sun lamp with elevation/azimuth,
  colour temperature via blackbody; one soft area light per room only when the room has no window
  (recorded as `assumed` in the manifest).
- `cameras.py` (pure Python placement, bpy only for creating the camera objects): per room three
  cameras at 1.4 m height, 24 mm on a full-frame sensor, 1920×1080: (1) in the free area (room polygon
  shrunk by 0.5 m minus proxy footprints grown by 0.3 m, shapely) looking at the centre of the longest
  wall; (2) from inside the door opening of the room (0.4 m into the room) looking at the room centroid;
  (3) from next to the largest window looking across the room. If a placement finds no free point it
  falls back to the room centroid and records a warning. Names `cam_<room id>_1..3`; the manifest lists
  per camera the position, target, and the ids of openings and furniture whose footprint centre is inside
  the frustum (needed by the final check later).
- `render.py`: Cycles, device OPTIX → CUDA → CPU fallback (printed), samples and resolution from CLI
  (job default 256 samples, 1920×1080, OIDN denoise; CPU tests 16 samples 320×180), passes Combined,
  Depth (Z), Normal, Object Index (every proxy and opening gets a unique pass index recorded in the
  manifest), file outputs: `renders/<cam>.png` (RGB), `renders/<cam>_passes.exr` (multilayer),
  `renders/<cam>_preview.jpg` (≤ 300 KB), `render_manifest.json` (camera, samples, device, seconds,
  pass index table). CLI `blender -b scene.blend --python wenart/blender/render.py -- --cameras all|cam_x
  --samples N --res WxH --out outputs/<p>/renders`.
- `wenart/blender/cli.py`: a small Python (outside Blender) wrapper that finds the Blender binary
  (`WENART_BLENDER` env, then `/workspace/tools/blender/blender`, then `/opt/wenart/blender/blender`,
  then PATH) and runs build/render with the arguments; the tests and the job use it.

## 4. Pod job `scripts/jobs/render.sh`

For each project in `projects/`: `python -m wenart.ingest.pipeline` → `python -m wenart.style ...` →
`wenart.blender.cli build` → `wenart.blender.cli render --samples 256` for every camera (time per view
logged), then copy to `$WENART_RESULTS`: previews, top-down level PNGs, manifests, report. Then
`pytest -m gpu tests/gpu/test_render.py` (GPU device was used; one 1920×1080 render under 4 minutes on
the A5000-class cards; passes exist and the depth pass has a sensible range; object index pass contains
every proxy index of the manifest). Everything persistent under `/workspace`, idempotent (skip renders
whose PNG exists unless `--force`). Assets cache in `/workspace/assets`.

## 5. Recognition follow-ups

- `wenart/recognition/tiles.py`: `drawing_extent(image) -> box` (ink bounding box of the page after
  removing the title and the dimension strip is NOT attempted; use the largest connected ink region
  cluster: binarise, close with a 25 px kernel, take the bounding box of the largest component group
  covering ≥ 60 % of the ink), `tiles(box, tile_px=1024, overlap=0.2) -> list[box]`, and
  `run_symbols_tiled(page, model, client)` in `bakeoff.py` (`--stage vlm --tiled`): one call per tile at
  full resolution (no downscale when the tile is ≤ 1600 px), boxes mapped back to page pixels, duplicates
  merged across tiles by IoU ≥ 0.5 (keep the higher confidence). Results in `results/bakeoff/*_tiled.json`
  and the summary gets a `symbols (tiled)` column. CPU tests on the synthetic scans with a fake client.
- `scripts/pod_setup_recognition.sh`: LibreDWG 0.14.1 first (`https://ftp.gnu.org/gnu/libredwg/libredwg-0.14.1.tar.xz`,
  fallback 0.13.3 when the download fails), version recorded in `dwg_roundtrip.json`.

## Tests

CPU (`pytest -m "not gpu"`, Blender at `/opt/wenart/blender/blender` is available here):
style profile table and defaults; asset API listing + one small download + manifest + licence refusal;
scene build for synthetic-01 L0 (object count per kind matches the JSON, every object has the custom
properties, booleans produced holes: a ray through each door centre hits no wall), proxies (size,
rotation, front wedge), camera placement (inside room polygon, outside proxies, three per room), a
320×180 16-sample CPU render of one camera (file exists, depth range plausible, index pass contains the
proxy indices), manifests validate against small schemas in `wenart/blender/schemas.py`; tiles (extent
on the synthetic scans, tile coverage, merge by IoU with a fake client).
GPU (`tests/gpu/test_render.py`): as in section 4.

## Done criteria

`pytest -m "not gpu"` green here; `scripts/gpu_run.py run --job scripts/jobs/render.sh` green on the
pod with 3 views × every room of the three synthetic projects rendered at 1920×1080 (previews committed
under `results/renders/`), `docs/progress.md` updated with render times and cost, every pod stopped.
