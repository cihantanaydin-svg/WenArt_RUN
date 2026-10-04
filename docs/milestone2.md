# Milestone 2 – recognition: synthetic projects, vector extraction, OCR/VLM bake-off

Goal: turn documents into the building JSON (`wenart/schema/building.schema.json`) with evidence,
and measure how well OCR and vision models read plan scans and phone photos. Everything that
cannot be verified against the source is marked `unverified`. No guessing.

Scope of this milestone:
1. Synthetic test projects with known ground truth (`wenart/synthetic`).
2. Vector path: DXF and vector-PDF extraction → building JSON, cross-checks, debug images (`wenart/ingest`).
3. Raster path bake-off on the pod: PaddleOCR vs Tesseract, Qwen3-VL-8B vs GLM-4.6V-Flash, two-pass
   agreement (`wenart/recognition`, `scripts/jobs/bakeoff.sh`).
4. Tests: CPU tests here, GPU tests on RunPod.

Out of scope: 3D, rendering, furniture assets, real DWG files from the user (the DWG round trip
LibreDWG `dxf2dwg` → `dwg2dxf` runs on the pod as part of the bake-off job).

## Conventions (all modules)

- Building frame: metres, X right, Y up, origin at the outer corner of the outer wall of level L0.
  Point = `[x, y]`. Rotation in degrees counter-clockwise around +Z.
- IDs: `L0`, `L1` ... levels; `w_L0_001` walls; `d_L0_001` doors; `win_L0_001` windows;
  `o_L0_001` plain openings; `r_L0_salon` rooms (ascii slug of the label, suffix `_2` on repeats);
  `f_L0_001` furniture; `c_001` conflicts.
- Walls are centre-line segments with `thickness`. In drawings a wall segment is a closed rectangle
  (LWPOLYLINE, 4 corners) on layer `DUVAR`; its long axis is the centre line, the short side the thickness.
- Openings are block inserts on layers `KAPI` (doors) and `PENCERE` (windows). Block names encode the
  clear width in cm: `KAPI_80`, `KAPI_90`, `PENCERE_120`, `PENCERE_180`, `PENCERE_60`. The insert point
  is the opening centre on the wall centre line; the insert rotation follows the wall direction.
  Door blocks contain the leaf (a line) and the swing arc; the arc side is the room the door opens into.
- Room labels are `TEXT` entities on layer `YAZI` placed inside the room: `SALON`, `YATAK ODASI`,
  `MUTFAK`, `BANYO`, `WC`, `HOL`, `BALKON`, `ANTRE`, `ÇOCUK ODASI`, `EBEVEYN YATAK ODASI`, `KİLER`.
  Optional area suffix: `SALON 24,50 m²`. Label → `room_type`: salon→living, yatak/çocuk/ebeveyn→bedroom,
  mutfak→kitchen, banyo→bathroom, wc→wc, hol/antre/koridor→hall, balkon→balcony, kiler/depo→storage,
  else other. `label` is the normalised Turkish label (title case, no area); `label_raw` the text as read.
- Level titles are `TEXT` on layer `YAZI` above the plan: `ZEMİN KAT PLANI`, `1. KAT PLANI`,
  `2. KAT PLANI`, `BODRUM KAT PLANI`, `MOBİLYA PLANI` (furniture plan), plus `ÖLÇEK 1/100`.
  Level label normalisation: `Zemin Kat`, `1. Kat`, `2. Kat`, `Bodrum Kat`; order = -1 for Bodrum,
  0 for Zemin, n for "n. Kat".
- Dimensions: `DIMENSION` entities (aligned) on layer `OLCU` along the outer walls. The measured length is
  the distance between the two definition points; the text override (if any) is what is printed.
  In vector PDFs a dimension is a line with ticks and a text like `3,45` (metres, comma decimal).
- Furniture: block inserts on layer `MOBILYA`. Block local frame: footprint rectangle centred at the
  origin, `size = [width (X), depth (Y)]`, front side = -Y (so `front_deg = (270 + rotation) mod 360`).
  Each block draws its rectangle plus a short line on the front edge. Block names and sizes (m):

  | Block | type | size |
  |---|---|---|
  | KANEPE_3LU | sofa | 2.2 × 0.9 |
  | KANEPE_2LI | sofa | 1.6 × 0.9 |
  | KOLTUK | armchair | 0.9 × 0.9 |
  | SEHPA | table_coffee | 1.0 × 0.6 |
  | YEMEK_MASASI | table_dining | 1.6 × 0.9 |
  | SANDALYE | chair | 0.45 × 0.45 |
  | TV_UNITESI | tv_unit | 1.6 × 0.45 |
  | KITAPLIK | bookshelf | 1.0 × 0.35 |
  | YATAK_CIFT | bed_double | 1.6 × 2.0 |
  | YATAK_TEK | bed_single | 0.9 × 2.0 |
  | KOMIDIN | nightstand | 0.5 × 0.4 |
  | DOLAP | wardrobe | 1.8 × 0.6 |
  | SIFONYER | dresser | 1.2 × 0.5 |
  | CALISMA_MASASI | desk | 1.4 × 0.7 |
  | TEZGAH | kitchen_counter | 2.4 × 0.6 |
  | BUZDOLABI | fridge | 0.7 × 0.7 |
  | OCAK | stove | 0.6 × 0.6 |
  | EVIYE | sink_kitchen | 0.8 × 0.5 |
  | LAVABO | washbasin | 0.6 × 0.45 |
  | KLOZET | toilet | 0.4 × 0.7 |
  | DUS | shower | 0.9 × 0.9 |
  | KUVET | bathtub | 1.7 × 0.75 |
  | CAMASIR_MAK | washing_machine | 0.6 × 0.6 |
  | BLOK_A, BLOK_B | unknown (footprint only, `unverified`) | as drawn |

  The table lives in code once: `wenart/synthetic/blocks.py: BLOCKS = {name: (type, width, depth)}` and
  `wenart/ingest` imports it (block-name → type is a lookup, never a guess; unknown names → `unknown` + `unverified`).
- DXF: `$INSUNITS = 4` (millimetres), model space, one level per file. Vector PDF: A3 landscape, scale 1:100,
  so 1 m = 10 mm = 28.3465 pt; page origin bottom-left; plan drawn with a fixed offset (x0, y0) in points
  that the truth file records. Line widths: walls 0.5 pt, furniture 0.25 pt, text Helvetica 8–10 pt.
- Raster pages: `scan` = the vector PDF rasterised with `pdftoppm -r 150 -gray`, rotated by a small random
  angle (−1.5°…+1.5°, seeded), light Gaussian noise, slight blur, saved as PNG. `photo` = the scan warped by
  a perspective transform (corners moved by up to 6 % of the size), uneven brightness gradient, JPEG quality 80.
  The truth file stores, per raster page, the 3×3 homography `H_building_to_pixels` (metres → pixels) so
  boxes can be compared.
- Evidence objects follow the schema. Vector methods use `layer` + `entity` (`"LWPOLYLINE:<handle>"`,
  `"INSERT:<handle>"`, `"TEXT:<handle>"`, `"DIMENSION:<handle>"`) for DXF and `entity = "path:<index>"` /
  `"char:<index>"` for PDF with `page`. Derived elements (room polygons, wall_id links) use `method = "derived"`
  and list the source entity in `entity`.
- Tolerances: vector geometry ±5 mm; area label vs computed ≤ 3 % → conflict with resolution "within tolerance",
  > 3 % → conflict and the room is `unverified`; dimension text vs measured ≤ 1 % → fine, else conflict.
- `status = needs_review` (stop) when: no scale source on a floor plan page, or the outer walls of a level do not
  form a closed loop (checked with shapely: union of wall rectangles must have exactly one exterior ring per level).
- Every page gets a debug image `outputs/<project>/debug/<doc>_p<page>.png`: the page raster (vector pages rendered
  at 100 dpi) with elements drawn over it, colour by method (vector green, ocr blue, ai orange, derived grey),
  alpha by confidence, unverified items dashed red. Written with Pillow/OpenCV.

## 1. `wenart/synthetic` (ground truth generator)

CLI: `python -m wenart.synthetic.generate --out projects` (idempotent, seeded, deterministic output).
Writes `projects/<name>/` with the documents, `brief.yaml` (when the project has one) and `truth/`:

- `truth/building.json`: schema-valid building JSON that the pipeline should reproduce (evidence entries
  point at the generated files; `status: ok`; `conflicts` lists the deliberate ones).
- `truth/pages.json`: `{"pages": [{"file", "page", "class", "kind", "level_id", "scale_metres_per_unit",
  "transform": {"kind": "affine"|"homography", "building_to_page": [...]}, "texts": [{"text", "box"}],
  "symbols": [{"id", "type", "block", "box", "rotation_deg"}]}]}` where boxes are axis-aligned
  `[x0, y0, x1, y1]` in page units (DXF: mm; PDF: points, origin bottom-left; raster: pixels, origin top-left).

Projects (from `docs/plan.md` §7):
- `synthetic-01` (brief: "Scandinavian, light oak floor, white walls, linen textiles, warm daylight"): L0 as
  `zemin_kat.dxf` (5 rooms: Salon 24,50 m² label, Mutfak, Yatak Odası, Banyo, Hol; furniture blocks in Salon,
  Yatak Odası and Banyo only), L1 as `1_kat.pdf` (vector, 5 rooms, no furniture) plus `1_kat_scan.png`.
  Outer footprint 9.6 × 7.2 m, outer wall 0.25 m, inner walls 0.10 m, ceiling 2.70 m (no section → warning).
- `synthetic-02` (no brief): one level, `plan_scan.png` (scan) and `plan_photo.jpg` (photo), 1+1 flat
  (Salon, Yatak Odası, Mutfak, Banyo, Antre), furniture in all rooms. Also writes the hidden source PDF to
  `truth/plan.pdf` (not a project document).
- `synthetic-03` (two style prompts in `brief.yaml: styles: [...]`): `kat_planlari.pdf` with 3 pages
  (Bodrum, Zemin, 1. Kat), and `mobilya_plani.dxf` (furniture plan for Zemin Kat: walls + furniture incl. one
  `BLOK_A` unknown block). Deliberate conflicts: one room label area 2 % off (within tolerance), one
  dimension text override 5 % off (conflict), and Zemin Kat appears both in the PDF and in the DXF
  (count cross-check, DWG/DXF wins).

Tests `tests/test_synthetic.py`: files exist, truth validates against the schema, DXF re-read with ezdxf has
the expected layers/blocks/inserts, PDF has the expected page count and text, raster sizes, determinism
(two runs produce identical truth JSON).

## 2. `wenart/ingest` (vector path → building JSON)

- `classify.py`: `classify_pages(project_dir) -> list[PageRecord]`; per file/page: `kind` (vector if the PDF page
  has paths and text, scan for images/PDF pages without a text layer, photo if the image has a non-rectangular
  page outline – OpenCV contour of the paper – or EXIF), `class` from keywords (`KAT PLANI`→floor_plan,
  `MOBİLYA`→furniture_plan, `KESİT`→section, `GÖRÜNÜŞ`→elevation, `VAZİYET`→site_plan), `level_label_raw`
  and `level_id`, scale from `ÖLÇEK 1/100` or `$INSUNITS`, with evidence. Raster pages without a text layer
  get `class: floor_plan, confidence 0.5` only when OCR/AI is available (M2 bake-off); otherwise `other` +
  `skip_reason`.
- `dwg.py`: `dwg_to_dxf(path) -> (dxf_path, converter_string)`: tries `dwg2dxf` (LibreDWG) then `ezdwg`;
  every output is read with `ezdxf.recover.readfile` and the audit errors are reported; failure → `needs_review`.
- `dxf_extract.py`: `extract_dxf(path, level_id) -> LevelExtraction` (walls, openings, room labels,
  furniture, dimensions, level title) with evidence per entity, in metres (via `$INSUNITS`).
- `pdf_extract.py`: `extract_pdf_page(path, page, level_id) -> LevelExtraction` from pdfplumber: wall
  rectangles from closed 4-segment paths with the wall line width, openings from the door/window glyph
  groups (leaf + arc / window double line), labels from words (merge chars, keep the rotation matrix),
  dimensions from the number texts next to tick lines; scale from the dimension texts vs measured lengths
  (`method: dimension_text`) with the `ÖLÇEK 1/100` text as cross-check.
- `rooms.py`: wall rectangles → shapely union → interior faces → polygons; label point-in-polygon → room;
  `area_computed`; `has_documented_furniture`; closed-outer-wall check.
- `pipeline.py`: `build_project(project_dir, out_dir) -> building dict`: classify → convert DWG → extract →
  rooms → link openings and furniture to walls/rooms → cross-checks (dimension vs measured, area label vs
  computed, counts across documents of the same level, outline across levels) → conflicts, unverified,
  warnings (ceiling height assumed 2.70 m) → validate against the schema → write `building.json`,
  `report.md` (tables: levels, rooms, furniture with source and status, conflicts, unverified) and debug images.
  CLI: `python -m wenart.ingest.pipeline projects/synthetic-01 --out outputs/synthetic-01`.

Tests: `tests/test_dxf_extract.py`, `tests/test_pdf_extract.py`, `tests/test_rooms.py`, `tests/test_classify.py`,
`tests/test_pipeline.py` compare against `truth/building.json`: same counts; walls matched by centre line within
5 mm and thickness within 5 mm; openings by type, centre within 10 mm, width within 10 mm; rooms by label with
area within 1 %; furniture by type, centre within 10 mm, size within 10 mm, rotation within 1°; conflicts and
unverified lists equal to the truth; the furniture-plan DXF of synthetic-03 wins over the PDF for Zemin Kat;
a project whose plan has no scale source → `needs_review`.

## 3. `wenart/recognition` + GPU bake-off

- `schemas.py`: JSON schemas for the model answers: `PageClass` (class, level_label_raw, scale_text,
  confidence), `TextItems` (list of {text, box}), `Symbols` (list of {type ∈ furniture enum ∪ {door, window},
  box, rotation_deg|null, confidence}), `RoomLabels` (list of {label_raw, box}). Strict: `additionalProperties: false`.
- `prompts.py`: one prompt per task, Turkish plan vocabulary explained in English, "answer only with JSON".
- `vlm_client.py`: OpenAI-compatible client for a local vLLM server (`http://127.0.0.1:8000/v1`),
  temperature 0, seed 0, structured output with the JSON schema (vLLM 0.30 `structured_outputs`; verify the
  exact request field in the vLLM docs at `raw.githubusercontent.com/vllm-project/vllm/v0.30.0/docs/`),
  image as base64 PNG, retries, timing per call.
- `ocr.py`: `ocr_page(image) -> list[{text, box, confidence}]` with PaddleOCR 3.7 (PP-OCRv5, `lang="latin"`
  or `"tr"` per the PaddleOCR docs, GPU) and `tesseract --oem 1 --psm 11 -l tur` (CPU) as cross-check;
  normalises Turkish characters and decimal commas.
- `detect.py`: `two_pass(page, model_a, model_b)`: run symbols with both models, match boxes by IoU ≥ 0.5 and
  equal type → `verified` (confidence = min), else `unverified` with both proposals kept in evidence (`pass` 1/2).
- `metrics.py`: text recall/precision (normalised, case-insensitive, digits with comma→dot), symbol
  precision/recall per type at IoU ≥ 0.5 (boxes mapped with the truth homography), page class accuracy,
  level label accuracy, per-page latency; `summarise(results) -> markdown table`.
- `bakeoff.py`: CLI `python -m wenart.recognition.bakeoff --projects projects --out results/bakeoff
  --models Qwen/Qwen3-VL-8B-Instruct zai-org/GLM-4.6V-Flash`: for every raster page in the synthetic
  projects (scan and photo), run OCR (both engines) and, per model, the page-class, room-label and symbol tasks;
  write `results/bakeoff/<project>_<page>_<model>.json`, debug images with boxes (`results/bakeoff/*.jpg`,
  small), `results/bakeoff/summary.md` and `summary.json`. The pod job starts/stops the vLLM server per model
  (`vllm serve <model> --port 8000 --max-model-len 16384 --limit-mm-per-prompt '{"image":2}'
  --gpu-memory-utilization 0.90`; wait for `/health`), models cached in `HF_HOME=/workspace/hf`.
- `scripts/pod_setup_recognition.sh` (idempotent, everything under `/workspace`): `/workspace/venv-vllm`
  (`vllm==0.30.0`, brings torch 2.13.0), `/workspace/venv-paddle` (`paddlepaddle-gpu` 3.x from the PaddlePaddle
  wheel index for CUDA 12.6, `paddleocr==3.7.0`), apt `tesseract-ocr tesseract-ocr-tur`, LibreDWG built from the
  GNU tarball (`https://ftp.gnu.org/gnu/libredwg/libredwg-0.13.3.tar.xz`, `./configure --disable-bindings
  --prefix=/workspace/tools/libredwg`, record the version), `HF_HUB_ENABLE_HF_TRANSFER=1` + `hf_transfer`.
  Time every step and print it; downloads of the two models (17.5 GB + 20.6 GB) are logged with MB/s.
- `scripts/jobs/bakeoff.sh`: setup → DWG round trip test (`dxf2dwg` on the synthetic DXFs, `dwg2dxf` back,
  compare entity counts; write `results/bakeoff/dwg_roundtrip.json`) → `pytest -m gpu tests/gpu/test_recognition.py`
  → bake-off → copy `results/bakeoff` into `$WENART_RESULTS` (small files only, JPG previews ≤ 300 KB each).
- `tests/test_recognition_cpu.py`: schemas accept/reject samples, two-pass matching logic, metrics on
  hand-made data, prompt/schema consistency. `tests/gpu/test_recognition.py` (`pytest.mark.gpu`): vLLM
  server answers `/health`, one classification call returns schema-valid JSON for a synthetic scan page,
  PaddleOCR reads at least 80 % of the room labels of `synthetic-02/plan_scan.png`.

## Done criteria

- `pytest -m "not gpu"` green here; `pytest -m gpu` green on the pod via `scripts/gpu_run.py run --job scripts/jobs/bakeoff.sh`.
- `results/bakeoff/summary.md` committed with the comparison table, and `docs/plan.md` §4.1/§4.2 picks confirmed
  or changed from the numbers. `docs/progress.md` updated. All pods stopped, run logged in `docs/gpu-log.md`.
