# Milestone 4 – furniture: library assets on the drawn footprints, AI layout for empty rooms

Goal: replace the proxy boxes with real furniture that keeps the drawn type, position, orientation and
footprint; furnish rooms the documents leave empty with an AI layout that passes deterministic checks;
measure the tiled symbol pass and the DWG round trip on the pod. Everything stays traceable:
`from_documents` pieces keep their evidence, `added_by_ai` pieces carry the model, pass and the checks
they passed.

Scope:
1. Asset catalogue and fitting (`wenart/furniture/catalog.py`, `fit.py`, `wenart/assets/models.py`).
2. Parametric fallback meshes and glTF import in Blender (`wenart/blender/furniture.py`, `parametric.py`).
3. AI layout for empty rooms with a rule-based placer (`wenart/furniture/layout.py`, `placer.py`,
   `prompts.py`, `schemas.py`) and the pod job `scripts/jobs/furnish.sh`.
4. Decor (cushions, plants, books) on documented furniture when the brief allows it (default yes),
   small and never on the floor polygon of a walkway.
5. TRELLIS.2 is NOT run in this milestone (its 24 GB requirement and setup are a separate test); types
   without a library match use the parametric fallback and are listed in the report as `fallback`.

Out of scope: AI polish, the final vision check, real-room photos.

## Conventions

- Building JSON stays the source of truth. Fitting never changes `footprint`, `front_deg`, `room_id`,
  `type` or `status` of a `from_documents` piece. A fit only adds `asset` (`library`, `asset_id`,
  `licence`, `fit_scale: [sx, sy, sz]`, `method: library|parametric`, `bbox_m`) and a note in the report.
- `added_by_ai` pieces: `source: "added_by_ai"`, `status: "unverified"` is wrong for them (they are not
  claims about the documents) → `status: "verified"` with evidence `{method: "ai", model, pass, text}`
  plus `checks: {inside_room, no_overlap, clearance_ok, doors_free, windows_free, wall_contact}` all true.
  Rooms with `has_documented_furniture: true` never get AI furniture (decor only).
- Asset frame: the piece's local frame is the block frame of Milestone 2 (width along X, depth along Y,
  front = -Y at rotation 0, origin at the footprint centre on the floor). Library models are re-oriented
  into that frame once, in `catalog.py` (`front_axis`, `up_axis`, `origin` offsets recorded per asset
  after inspecting the model's bounding box; Poly Haven models are Z-up, metres, origin on the floor).
- Fitting rule (plan §4.8): among the catalogue entries of the piece's type, pick the one whose bounding
  box aspect `width/depth` is closest to the footprint's; scale to the footprint on X and Y, Z scaled by
  the mean of X and Y (height follows the piece); non-uniform scale (max/min of sx, sy, sz) above 15 %
  → next candidate; no candidate within 15 % → parametric fallback (exact fit, always). Every fit is
  logged: asset id, licence, scale factors, aspect error, `method`.
- Library: Poly Haven models (CC0) are the only online source in this milestone (`GET
  https://api.polyhaven.com/assets?type=models`, `/files/{id}` → `gltf` at `1k`, `/info/{id}`). The
  catalogue maps our furniture types to concrete asset ids, chosen by hand from the catalogue after
  inspecting the model list, with bounding boxes measured from the downloaded glTF (`wenart/furniture/
  catalog.json`: id, type, source, licence, bbox_m, front_axis, up_axis, origin_offset, url). Only CC0.
  Types with no usable model (toilet, washbasin, shower, bathtub, fridge, washing_machine,
  kitchen_counter, kitchen_island, stove, sink_kitchen, wardrobe, dresser, tv_unit if none fits) use the
  parametric fallback and are listed in `catalog.json` as `{"type": ..., "parametric": true}`.
- Parametric meshes (Blender, `wenart/blender/parametric.py`): simple but recognisable shapes built from
  the footprint and type height: bed (mattress, frame, headboard on the back side, two pillows), sofa
  (seat, back, two arms, cushions), armchair, table (top + 4 legs), chair (seat, back, 4 legs), desk,
  wardrobe (box, two door panels with handles), dresser/nightstand/tv_unit/bookshelf (box with drawers or
  shelves), kitchen_counter (box, worktop overhang, plinth), kitchen_island, fridge (box, handle), stove
  (box, four rings), sink (box + basin cut), washbasin (basin on a pedestal), toilet (bowl + tank), shower
  (tray + glass panels), bathtub (tub with inner cut), washing_machine (box + round door), unknown (the
  Milestone 3 proxy box, striped). Materials from the style (wood for frames, fabric colour from the
  style's textiles slot, white ceramic for sanitary ware, steel for appliances).
- Decor (`wenart/furniture/decor.py`): rule-based, only when `brief.decor` is not false: cushions on
  sofas and beds (parametric: the CC0 pillow model lies flat and squashed to a standing cushion looks
  wrong), books on shelves and desks (parametric), one potted plant per living room / bedroom in a free
  corner (library `potted_plant_*` models, CC0, scaled to 0.4 m), rugs are skipped. Decor
  pieces are `added_by_ai` with `method: "rule"` and never larger than 0.6 m; they are listed in the
  report and in the scene manifest with `kind: decor`.

## 1. Catalogue and fitting

- `wenart/assets/models.py`: `fetch_model(asset_id, out_dir, size="1k") -> dict` (glTF + textures into
  `assets/models/<id>/`, manifest entry with licence CC0, files, sha256, bbox measured from the glTF
  accessor min/max in metres, idempotent), `verify_catalog()` lists the ids on the API without downloads.
- `wenart/furniture/catalog.py`: loads `catalog.json`, `candidates(type) -> list[entry]`,
  `bbox_aspect(entry)`; `wenart/furniture/fit.py`: `fit_piece(piece, catalog) -> fit dict` (pure), `fit_building(building, catalog) -> building`
  (adds `asset` to every `from_documents` piece and `added_by_ai` piece, never anything else), `fit_report(building) -> markdown`.
- CLI: `python -m wenart.furniture.fit outputs/<p>/building.json --catalog wenart/furniture/catalog.json --out outputs/<p>/building_fitted.json --assets assets`
  (downloads the needed models into `assets/models`, falls back to parametric when offline and says so).

## 2. Blender

- `wenart/blender/furniture.py`: for every furniture piece, import the fitted glTF (`bpy.ops.import_scene.gltf`),
  re-orient to the piece frame, apply `fit_scale`, place at `footprint.center` on the floor of the level,
  rotate by `footprint.rotation_deg`, name `furn_<id>` with the custom properties of Milestone 3 (`wenart_id`,
  `wenart_kind: furniture`, `wenart_status`, plus `wenart_source: from_documents|added_by_ai`, `wenart_asset`);
  or build the parametric mesh. The Milestone 3 proxy box stays available with `--proxies` and for
  `unknown` pieces. Unverified pieces keep the red stripes (as a material overlay on the asset).
- The scene manifest gains per piece: `asset`, `fit_scale`, `method`, `bbox_m`, `decor: [...]`.
- Cameras: the free-point search uses the fitted bounding boxes (not only footprints) and ignores decor.
- Pass indices: one per piece (decor shares its host's index; a plant on the floor has its own).
- Glass inside a room (shower panels) is a thin pane (transparent + glossy by Fresnel): Cycles' depth and
  index passes see through it; window panes keep the Glass BSDF.

## 3. AI layout for empty rooms

- `wenart/furniture/prompts.py` + `schemas.py`: one prompt per room type (living, bedroom, kitchen,
  bathroom, wc, hall, other) in English with the Turkish room label, the style text, the room polygon in
  metres, the door openings (with swing side) and windows (with sill height) as a compact JSON, the
  allowed types for that room type, and the size table (`wenart/synthetic/blocks.py` sizes are the
  defaults; the model may choose from 3 size options per type). Answer schema: `{"pieces": [{"type", "center":
  [x, y], "rotation_deg", "size": [w, d], "against_wall": bool, "reason"}]}`, strict, max 12 pieces.
- `wenart/furniture/layout.py`: `propose_layouts(room, building, style, client, passes=2)` calls the
  VLM twice (pass 1 and pass 2 with a different instruction order and seed) through the existing
  `wenart.recognition.vlm_client` (text-only request is fine: no image, or the top-down level PNG of
  Milestone 3 when available), temperature 0, structured output; `placer.py` validates each proposal
  deterministically with shapely: every footprint inside the room polygon shrunk by 2 cm; no overlap
  between pieces; clearance 0.6 m in front of beds, sofas, desks, wardrobes and 0.9 m walkway from every
  door to every other door/window of the room; door swing arcs free; windows: nothing taller than the sill
  within 0.3 m of a window wall segment (beds, sofas, tables allowed under windows); `against_wall`
  pieces (bed headboard, wardrobe, sofa back, kitchen counter) touch a wall within 5 cm; repair steps
  (snap to the nearest wall, slide along the wall, shrink to the next size option, relocate to another wall,
  drop the piece) with at most 40 iterations, every repair logged; when the room's anchor piece (bed, sofa,
  counter, toilet, washbasin) was dropped, it is placed alone, locked, and the rest is placed around it
  (`anchor_first`); types the room type does not allow are rejected before placement. The result is the
  proposal with the fewest dropped pieces
  (ties: pass 1); pieces present in both proposals (same type, centre within 0.5 m) get confidence 0.9,
  others 0.6. Pieces added: `added_by_ai`, evidence `{method: "ai", model, pass, text: <reason>}`, `checks`
  recorded. Empty result (model answered nothing usable) → the room stays empty and the report says so.
- CLI: `python -m wenart.furniture.layout outputs/<p>/building.json --style outputs/<p>/style.json --server
  http://127.0.0.1:8001/v1 --model Qwen/Qwen3-VL-8B-Instruct --out outputs/<p>/building_furnished.json
  --debug outputs/<p>/layout_debug/` (top-down PNG per room with the proposal, repairs and final layout).
- Pod job `scripts/jobs/furnish.sh`: setup (reuse `scripts/pod_setup_recognition.sh`), start the Qwen
  vLLM server as in `bakeoff.sh`, for each project: pipeline → style → assets → fit → layout (empty rooms)
  → decor → build (with assets) → render → GPU tests (`tests/gpu/test_furnish.py`: every empty room of
  synthetic-01 L1 got at least a bed or a sofa where its type calls for it, all checks true, no piece
  blocks a door, server latency per room logged). Results and previews copied as in `render.sh`.

## Tests

CPU: catalogue validation (every id exists on the API in a listing test, bbox and frame fields present),
fitting on the synthetic buildings (every from_documents piece gets an asset or parametric fallback,
footprint untouched byte for byte, scale cap respected, report lists fallbacks), parametric meshes in
Blender (bbox equals the footprint ± 1 cm, origin on the floor, front marker side), glTF import of one
small downloaded model (ArmChair_01 1k, ≤ 20 MB) with re-orientation (bbox after import matches
catalog bbox), placer with hand-made proposals (overlap, door block, window block, wall contact, repairs,
drop), layout end-to-end with a fake client, decor rules, schema strictness, scene manifest fields.
GPU: `tests/gpu/test_furnish.py` as above.

## Done criteria

`pytest -m "not gpu"` green here; `scripts/gpu_run.py run --job scripts/jobs/furnish.sh` green on the pod
with furnished renders of synthetic-01 (both levels) and synthetic-03 in `results/renders/`, the fit and
layout reports committed under `results/furniture/`, `docs/progress.md` updated, every pod stopped.
