# Milestone 12 – track B: library audit and growth scaffolding (as built)

Design: `docs/milestone12.md` §6 (D21–D24), §1.6 (diagnosis), §1.7 B2, §8 (pods P2, P3, P4), contracts §13. Cloud session,
CPU only, 10 Oct 2026. No pod was started; no model file was downloaded (API metadata only).

## 1. What was built

| Part | File: function | What |
|---|---|---|
| U3 (now) | `wenart/assets/audit/write.py: licence_removals`, `note_u3`; CLI `audit licences --write` | the 18 NC / SA Objaverse models of `catalog_library.json` carry `audit = {status: removed, reasons: ["licence <id> not allowed (user decision of 10 Oct 2026)"], fixes: {}, version: m12, checked_utc}`; files stay on the volume; a line in the catalogue's `notes`; `catalog.usable()` is false for them |
| B2 | `wenart/assets/objaverse.py: GENERATED_VIA`, `catalog_entry`; `write.py: generated_credit` | the 281 generated entries' `via` = "generated for WenArt_RUN (TRELLIS.2-4B, MIT, from a Z-Image-Turbo image, Apache-2.0)" (was the Objaverse line); `write-catalog` writes it for new generated entries. The `ATTRIBUTION.md` writers (`wenart/run/copy.py`) use `attribution`, which was already right |
| Size table (D23) | `wenart/recognition/size_table.yaml`; `wenart/furniture/sizes.py: real_range, product_size, fits` (frozen signatures) + `types, decor_types, products, is_run, range_error, scale_to_fit, oriented_fits, reload` | per furniture type width, depth (as before, readers unchanged), **height**, a default **product** (w, d, h), standard **products** (footprints), `run` for counters / wall cabinets; a **decor** block for the 21 library decor types (`cushion` or `decor_cushion`); every change has its source in the file |
| Items | `wenart/assets/audit/items.py: load_items, item_of, has_front, model_file` | both catalogues (library + Poly Haven) as one record shape |
| Title words | `wenart/assets/audit/keywords.py: fold, named_families, flags, title_check, suggested_type` | type families in EN / TR / DE / NL / FR / ES / IT (+ SV, RU, CJK words met in the titles), longest keyword wins, near types, flags `outdoor`, `crude`, `wrong`, `part`, `scene` with exceptions ("indoor", "garden stool", "King Street") |
| Code checks | `wenart/assets/audit/checks.py: run_checks, item_checks, size_check, pivot_check, title_check, title_size_check, mesh_check, texture_check, duplicates, licence_reason, geometric_front` | §6.1 code checks; work on the catalogue fields alone (dry) or with the render's measurements |
| Mesh | `wenart/assets/audit/meshstats.py: analyse` | numpy only (runs in Blender and in the tests): faces, zero-area faces, open and non-manifold edges, inconsistent winding (flipped normals), loose parts, parts outside the main body (open drawers, `front_outside`), box, pivot |
| Render (P2) | `wenart/assets/audit/render.py: person_boxes, seat_bar_boxes, grid_lines, reference_layout, camera_specs, render_jobs, run_render, deal, compose_sheet, compose_all, texture_jobs, texture_overlay`; `wenart/assets/audit/blender_audit.py: main, one, texture_one` | 4 views (front 3/4, side from +X, top, back) at 512 px of every model at its catalogue scale on a grey floor with a 0.5 m grid (0.1 m for items < 0.6 m), a 1.75 m person (blue) and a 0.45 m seat bar (orange) on the model's left; sheet 1024 px with a header: id, type, source, licence, W x D x H, the scale reference, the title; resume by `job_sha`; N Blender workers; texture sets as 1 m samples with a 10 cm grid |
| Vision (P3) | `wenart/assets/audit/ask.py: schema, schema2, prompt, prompt2, build_requests, model_of, ask, load_answers` | strict JSON, temperature 0, seed 0; pass 1 asks type (+ what instead), one object, real product, indoor / outdoor, upright, size plausible, open drawer, styles, quality 1–5 with anchors, front side, bedding / pillows / cushions, decor contact; pass 2 = type only; answer store and workers of `objaverse.judge_ask`; model = a check.yaml key (dotted keys such as `bakeoff.fp8` too); `--serve` starts the server with `wenart.run.servers` |
| Decisions | `wenart/assets/audit/decide.py: decide, expected_status, answer_flags` | keep / fix / remove per §6.1 + `pending` (dry only) with the expected outcome |
| Sheets | `wenart/assets/audit/sheets.py: contact_sheet, grid` | one sheet per type, border green / amber / red / grey, id and first reason |
| Gaps | `wenart/assets/audit/gaps.py: gap_table, gaps_markdown, groups_from_yaml, merge_groups` | per room type and style family: kept models vs target (anchor >= 5, partner >= 3), the sources per gap; reads track G's `groups.yaml` (its shape is tested) plus the built-in decor and light rows |
| Writer | `wenart/assets/audit/write.py: apply_decisions, fix_entry, summary` | `audit` record + fixes into catalogue fields (`rescale`, `front_quarter_turns`, measured box / `origin_offset`, `type`), `audit.before` keeps old values, flags `real_product`, `has_bedding`, `has_cushions`, `has_pillows`, `contact`; idempotent (`decision_sha`) |
| Tables | `wenart/assets/audit/report.py: rows_of, audit_json, audit_csv, audit_markdown, write_outputs` | `audit.json`, `audit.csv`, `audit.md` |
| CLI | `wenart/assets/audit/cli.py`; `wenart/assets/__main__.py` dispatch | `python -m wenart.assets audit licences | render | code | ask | decide | sheets | gaps | write | dry | status` |
| Growth (D24) | `wenart/assets/audit/growth.py: polyhaven_candidates, abo_candidates, gso_candidates, infinigen_plan, approved, cmd_ingest` | `python -m wenart.assets growth <polyhaven|abo|gso|infinigen> list | plan | ingest`; ingest refuses without `results/library/growth/approved_<source>.json` (`approved_by`, `approved_utc`, `ids`) |
| Settings | `wenart/assets/audit.yaml` | thresholds, render, ask model key (`agent` until the bake-off picks), gap targets |
| Pod jobs | `scripts/jobs/library_audit_render.sh` (P2), `scripts/jobs/library_audit_judge.sh` (P3) | job conventions of `agent_check.sh`; results copied after every step and from the EXIT trap; resume after a cut |

## 2. Decisions within the design

- **Size rule** (D23, §6.1 "unfixable proportions" / "size off by 15–30 %"): the audit asks for the uniform scale nearest
  1 that puts the box (w along the front, d, h) inside the type's real ranges (each widened by 3 %). None → the front
  turned 90° may fit (fix `front_axis`, toward the geometric front of the M8 note when it names one) → another axis up
  may fit (remove: "lies on its side"; the up axis is no catalogue field) → remove "proportions". Scale within 15 %:
  ok; 15–30 %: fix (rescale); beyond 30 %: fix when the units were guessed, remove for a known-unit product.
- **Retype as a fix**: a real product filed under the wrong type ("armadio", "Armoire" as tall cabinets) is a `fix`
  (`type`) when the title names one type of the same kind, its box fits that type and the vision check does not say
  it is the filed type; without a single named type it is removed.
- **Vision rules** (CLAUDE.md, §10 risk row): a titled model stays only when the title does not conflict and pass 1
  says it is the type; a model whose title names no type (generated models, "Lpuvw") stays only when pass 1 and the
  independent pass 2 agree (pass 2 is asked only for those). Near types agree ("sofa" / "sofa_corner").
- **Crude**: furniture below 3,000 triangles is removed unless the vision quality is >= 4 (ABO and Poly Haven boxes
  with textures are expected to stay; uploads to go).
- **Not a real product** (vision) and quality < 4 → removed; quality <= 2 → removed; open drawer / door or a loose
  part → removed; outdoor → removed.
- **Duplicates**: same type, box ± 1 cm, faces ± 1 % and the same texture (hash on the pod; before it the material
  colours of recolour.py, so ABO colour variants stay); the same GLB sha256 across types too. The ABO / Poly Haven /
  Objaverse / generated order, then the judges' quality, keeps the first.
- **Crib front**: the size table's crib width / depth were swapped to the layout's convention (front = long side,
  `schemas.SIZE_OPTIONS`); readers accept either orientation (only an unfronted crib's orientation follows it).
- **Catalogue writes on the pod go to copies** (`AUDIT_ROOT/audit/catalogue/`): the lead copies them into
  `wenart/furniture/` after the user's OK of the removals (§9 step 5). The dry audit is never written (`write` refuses
  `mode: dry`).
- **Contact sheets of the dry audit** use the M10 thumbnails (128 px tiles); the pod sheets use the audit's front 3/4
  view.

## 3. Size-table changes (all in `wenart/recognition/size_table.yaml` with their sources)

| Row | Change | Source |
|---|---|---|
| crib | width / depth swapped: [1.15, 1.50] x [0.60, 0.85] | layout `SIZE_OPTIONS` 1.26 x 0.66 .. 1.46 x 0.76 (front = long side) |
| dresser | width min 0.80 → 0.70, depth min 0.40 → 0.35 | ABO B079X4CP3F (72 x 75 x 36 cm chest), B01557QQSW (98 x 90 x 38 cm) |
| tall_cabinet | depth min 0.30 → 0.25 | ABO B07RMJPJMX "Colonna da bagno, 30 x 27 x 140 cm" |
| floor_lamp | [0.25, 0.60] → [0.20, 0.70] both | ABO B07374K536 adjustable task lamp, box 0.24 x 0.62 x 1.63 m |
| bar_stool | width max 0.50 → 0.60, depth max 0.50 → 0.70 | ABO bar stools 0.38–0.57 x 0.36–0.66 m, B075YQ478W 0.49 x 0.66 x 1.08 m; the library's own range (objaverse.yaml) |
| heights (new) | from `objaverse.yaml types` (product ranges), except bathtub [0.40, 0.80] → [0.40, 0.72], wardrobe [1.40, 2.60] → [1.50, 2.45], table_dining [0.65, 0.85] → [0.65, 0.92]; kitchen_counter [0.85, 0.95], kitchen_island [0.85, 1.10]; stair none | std (built-in tubs 0.55–0.60 m, freestanding to 0.72; wardrobes 1.8–2.4 m, ABO 1.81–2.26; ABO dining tables 0.66–0.96; base units 0.85–0.90 + worktop) |
| products (new) | default product per type (ABO median box where ABO has products) and standard footprints (the layout sizes first) | `SIZE_OPTIONS`, std, ABO medians |
| decor (new) | 21 decor types: footprint, height, product | `objaverse.yaml decor_sizes` + heights; ABO medians |

Review result: of the 77 ABO titles with sizes in cm, 72 fit the old table; the other 5 are two chests and a bathroom
column (ranges widened), a wardrobe filed as a tall cabinet (retyped by the audit) and a desk whose box is not its
title's (listing variant). Over all ABO and Poly Haven boxes, after the changes 6 real products are still outside:
a 0.36 m deep "coffee table" (removed: proportions), two Edgewest chaise sectionals whose documented front is a short
side (fix: front turned to the geometric front), a Poly Haven low "desk" (removed), a school desk and a worn bookshelf
(fix: rescaled 23 % and 25 %).

## 4. U3: the 18 removed models (catalogue only; GLBs stay on the volume)

| Licence | n | Models (type: title) |
|---|---|---|
| CC-BY-NC-4.0 | 7 | wardrobe "Traditional Mennonite corner cabinet", fridge "Haier Refrigerator", toilet "CWLCCST1-6DT01 Ld", bathtub "CARBAWH1-6DT01", bench "Street Wooden Bench", candle "Medieval candle", pendant light "Small Chandelier" |
| CC-BY-NC-SA-4.0 | 5 | ottoman "Decor, footrest", bench "Mainstreet USA Bench", books "Book", books "Box on Ready Player Two", books "The Woodbook #3DST29" |
| CC-BY-SA-4.0 | 6 | washbasin "Bathroom", toilet "Zenit Close Coupled Push Button Flush Toilet", toilet "Memoirs Stately Close Coupled Toilet", bench "City Bench 001", books "Books", books "Opened comics book" |

## 5. CPU dry audit (catalogue fields only; `results/library/audit/dry/`)

`python -m wenart.assets audit dry` over 1,066 models (1,032 library + 34 Poly Haven). `removed` / `fix` decided by code;
`removed?` / `fix?` / `keep?` expected once the vision check answers; `vision?` = no title evidence (two passes decide).

| Source | keep? | fix? | vision? | removed? | removed | total |
|---|---|---|---|---|---|---|
| ABO | 513 | 4 | 8 | 0 | 13 | 538 |
| generated | 0 | 15 | 243 | 0 | 23 | 281 |
| Objaverse | 110 | 7 | 21 | 11 | 64 | 213 |
| Poly Haven | 30 | 2 | 1 | 0 | 1 | 34 |
| **all** | **653** | **28** | **273** | **11** | **101** | **1,066** |

- Removed by code (first reason): proportions no real piece has 26 (23 generated: 15 bathtubs 0.80 m high, beds,
  stoves), title flags 26 (Objaverse 20: park / street / city benches, street lamps, low poly, stylized, "test", a
  scene; ABO 6: the "Luchtbed" air bed, 5 "Bagley Sectional Component"), title names another type 26 (Objaverse 24:
  "Window" as curtains, "Bathroom" as washbasins, ceiling lamps / a sink / a cutting board / a basket as trays, a
  grandfather clock, a wall sconce, "MESA COMEDOR" as a coffee table ...; ABO 2: "Aparador con vitrina", a dressing
  table, both filed as tall cabinets), licence 18 (U3), duplicates 5 (4 ABO pillow / mirror copies, 1 Objaverse).
- Fixes expected: front turned 17 (all 10 bunk beds faced their long side, 3 toilets, the 2 Edgewest sectionals, a
  kitchen sink, a crib), rescale 7 (3 shoe cabinets, a double bed, a crib, a desk, a bookshelf), retype 4 ("Armoire",
  "armadio" → wardrobe, "Rattan Tray" filed as a basket → tray, "Laundry Basket" filed as a tray → basket) once the
  vision check agrees.
- Expected removals after the vision check: 11 (crude Objaverse uploads below 3,000 triangles, "Dining Set", "A table,
  chairs & few cups", "Scene").
- Waiting for the vision check: every model (671 titled), 258 generated + 36 untitled models need two passes, 56
  low-face models (ABO / Poly Haven expected to stay).
- Gaps (`gaps.md`, built-in groups; generated models not counted until their two passes): 250 of 504 (type, family)
  cells below target; empty for every family: bathtub, shower, washing machine, throw, plant_large, bowl (generated
  or Objaverse only); kitchen and bath fixtures, non-modern sofas, beds, lights and wall art thin.

## 6. Growth lists (metadata only; `results/library/growth/`; nothing downloaded)

| List | Candidates | Size | Notes |
|---|---|---|---|
| `candidates_polyhaven.json` | 88 unused CC0 models of our types (pendant lights 8, vases 8, sculptures 10, chairs / stools 13, tables 12, shelves 5, cabinets 7, wall art 5 ...) | 501 MB at 2k glTF | type from the API category path, first type whose real size holds the API dimensions; 17 marked `fits_real_size: false` (the audit decides) |
| `candidates_abo.json` | 232 picks of 2,088 found: style pass 82 (classic 31, industrial 27, rustic 24: armchairs, chairs, sofas, sectionals, side tables ...), decor pass 120 (40 pillows, 40 rugs, 40 wall art), 30 headboards | 7.8 GB | colour variants picked once; ABO has no kitchen / bath fixtures |
| `candidates_gso.json` | 73 found, 36 picked (bowls 12, plant pots 15, baskets 7, tray 1, books 1) | 239 MB | HF mirror `suvadityamuk/google-scanned-objects-raw` (file names; no licence tag on the mirror: CC BY 4.0 of GSO to confirm per object); mugs and towels listed without a type |
| `plan_infinigen.json` | test batch: toilet, bathtub, bathroom sink, kitchen sink, oven, beverage fridge (3 seeds each) + dishwasher, microwave, cabinet, books, bowl, pot | ≈ 1.5 GB tools, no model files | BSD-3 (LICENSE read), Python 3.11 + bpy 4.2.0 (pyproject.toml read); factory paths moved on main: listed on the pod first |

## 7. Pods (commands for the lead)

P2 (render + code; no vision model; default 30 GB container disk):

    python3 scripts/gpu_run.py run --job scripts/jobs/library_audit_render.sh --gpu 'RTX PRO 6000' --max-minutes 110 \
      --purpose "M12 P2: library audit A (renders with scale reference, mesh and code checks)"

Expected 45–70 min (setup 5–8, Poly Haven models 1, smoke render of 4 models 2, 1,066 models at ≈ 4 s each over 3
Blender workers ≈ 25–35, texture samples ≈ 3, sheets and code checks ≈ 3, GPU tests 1); worst case 110 min ≈ $4.6 at
$2.49/h. A cut pod resumes with the same command (measurements are reused by `job_sha`). The smoke step stops the job
within minutes if the Blender side fails (it was not run in the session: no Blender here).

P3 (vision, decisions, sheets, gaps, catalogue copies; needs P2's `/workspace/library-audit/audit/` on the volume):

    python3 scripts/gpu_run.py run --job scripts/jobs/library_audit_judge.sh --gpu 'RTX PRO 6000' --disk 150 \
      --max-minutes 80 --env AUDIT_MODEL_KEY=agent \
      --purpose "M12 P3: library audit B (vision check, decisions, sheets, gaps)"

`AUDIT_MODEL_KEY` = the bake-off's pick (a check.yaml key: `agent`, or a dotted `bakeoff.<name>` once track A's
servers.py is merged; for the 2-GPU model add `--gpu-count 2 --over-5-ok`). Expected 40–60 min (setup 8–12, server
3–5, pass 1 ≈ 1,066 calls at 4 workers ≈ 20, pass 2 ≈ 300 calls ≈ 5, decide / sheets / gaps / write ≈ 3); worst case
80 min ≈ $3.3 (1 GPU) or ≈ $6.6 (2 GPUs). Results: `results/library/audit/` (audit.json/.csv/.md, contact sheets,
gaps, answers, `catalogue/` copies).

## 8. Tests added

| File | Tests | What |
|---|---|---|
| `tests/test_library_sizes.py` | 13 | table completeness, products inside their ranges, layout sizes in the front convention (crib: fails on the old table), height in `fits` (the stub ignored it), `product_size` orientation and runs, the 77 ABO titles, the changed rows' sources, old readers |
| `tests/test_audit_keywords.py` | 51 | languages, compounds, verdicts, flags and their exceptions, longest match, retype suggestion |
| `tests/test_audit_checks.py` | 20 | licence, size rule (rescale / remove / side / front turn), pivot, up, title, title size, crude, mesh and texture records, duplicates and colour variants, mesh measurements on cubes (flip, seam, drawer, zero area, non-manifold) |
| `tests/test_audit_decide.py` | 19 | decisions and flags; U3 and B2 on the committed catalogue (fail on the old one); writer idempotence, front turn and retype keep `catalog.validate` |
| `tests/test_audit_render.py` | 10 | person 1.75 m, bar 0.45 m, grid, layout, cameras, round robin, resume by `job_sha` (a failure tried once more), Blender processes, a model that stops Blender recorded and the rest rendered, sheet header, texture grid |
| `tests/test_audit_ask.py` | 6 | strict schemas, the question's facts, request hash, dotted model keys, fake-client ask with reuse and staleness |
| `tests/test_library_growth.py` | 7 | contact sheet, gap table, groups.yaml shapes (track G's too) and the merge, Poly Haven list from canned API answers, the committed list, GSO / ABO / Infinigen helpers, the ingest gate |
| `tests/test_audit_cli.py` | 3 | licences step, the dry audit end to end on a small catalogue, `python -m wenart.assets` dispatch |
| `tests/test_library_jobs.py` | 5 | job conventions of both scripts, P3 writes copies only, P3 stops without P2 |
| `tests/gpu/test_library.py` | +4 | P2 / P3 outputs on the pod (`-k audit_render`, `-k audit_judge`) |

## 9. Left / open

- The Blender side (`blender_audit.py`) and the texture samples were not run (no Blender in the session); P2's smoke
  step and GPU tests cover them.
- P4 (growth after the user's OK): the ingest for Poly Haven (fetch) and ABO (GLB download) exist behind the approval
  gate; adding the new models to the catalogues (Poly Haven entries in `catalog.json`; ABO through the survey /
  `write-catalog` path), GSO conversion and the Infinigen batch are P4 work.
- The vision model is `agent` until the bake-off picks one (`wenart/assets/audit.yaml ask.model_key` or `--env
  AUDIT_MODEL_KEY=`).
- The pod copy `results/library/catalog_library.json` (M10 output) was left as written; the runtime catalogue is
  `wenart/furniture/catalog_library.json`.

## 10. Changes needed in other tracks' files

| Track | File | Request |
|---|---|---|
| S | `wenart/furniture/fit.py`, `catalog.py` | read the real sizes (heights, products) from `wenart.furniture.sizes` for the real-size rank (D23: one table) instead of `objaverse.library_size_table`; use the flags `real_product`, `has_bedding`, `has_pillows`, `has_cushions`, `contact` once P3 writes them; optionally validate the `audit` record (status keep / fix / removed, reasons list) in `_validate_model` |
| R | `wenart/recognition/symbols.py` (`oriented_size`) | the crib's width is now its long side (front), as the layout builds it: an unfronted drawn crib turns 90° vs before; check R's crib cases; `sizes.product_size` is ready for misread fixed equipment |
| A | `wenart/run/copy.py` (`library_attribution`) | optional: mark audit-removed models in `ATTRIBUTION.md` (they stay credited while thumbnails show them); `scripts/pod_setup_polish.sh` must download a dotted `AGENT_MODELS` key (`bakeoff.<name>`) for P3 with a bake-off model |
| Lead | `docs/milestone12.md` §6.3 | the table lives at `wenart/recognition/size_table.yaml` (contract §13.1–13.2), not `wenart/furniture/size_table.yaml` |
| Lead | after P3 and the user's OK | copy `results/library/audit/catalogue/*.json` into `wenart/furniture/`; commit `results/library/growth/approved_<source>.json` for each approved list (fields `source`, `approved_by`, `approved_utc`, `ids`) |
