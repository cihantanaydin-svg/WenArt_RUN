# Milestone 7 – real projects in: CAD PDFs in feet or metres, DWG, scans and photos; style-true furniture, AgX Punchy, better checks

Goal: the user's first real project (`projects/real01/real01.pdf`, an AutoCAD 2018 PDF of a 30' × 50' Indian house
plan) runs from the project folder to final, checked renders with the same one command as the synthetic projects;
DWG files and scanned or photographed plans stop ending in `needs_review` by default; and the decisions of
3 Oct 2026 (items 3, 5, 6, 7, 8, 9 in `docs/progress.md`) are built. The no-hallucination rules stay as they are:
geometry comes from vector entities (or, for rasters, from deterministic image processing), AI only names what the
geometry already shows (two passes that must agree, checked against size tables), and everything else is
`unverified`, `assumed` or a listed conflict.

Research and prototypes (3 Oct 2026, session scratch, not committed):
- real01 (`pdfplumber`): 1 page, 842 × 595 pt, 163 chars, 27,259 lines, 9,592 curves, 26 tiny rects, no images, no
  layers, line widths only 0.72 and 0. Walls are **21,512 hatch lines at 45° (spacing 0.12 pt)**, i.e. visually solid;
  wall outlines are 0°/90° black strokes. The two overall dimensions are red lines with filled red arrowheads and the
  texts `50'` and `30'` (23.2 pt high) in a gap of the line: 621.8 pt ↔ 50 ft and 373.1 pt ↔ 30 ft, **12.436 pt/ft
  both (0.01 % apart)**. Room labels are two runs each (`Bed Room` / `11' x 10'`, `Bath+` / `Toilet` / `7' x 5'`).
  Furniture is exploded blocks: black strokes, a golden stroke colour (0.646, 0.486, 0) for the dining chairs, 1,008
  zero-length grey "dots" for the chair seats, green fills for the garden plants outside the house.
- A wall mask rasterised from the hatch lines at 4 px/pt (closing 3 × 3) is clean: one component for the plot
  (compound) wall, ten for the house walls, a few specks (lamp symbols drawn with 45° strokes). Thickness histogram:
  ≈ 6.5″ and ≈ 9.3″ walls. The plot wall is a separate component not touching the house; it is open on the right
  below the garden strip (the gate side of the parking).
- The same plan rasterised at 150 dpi, thresholded (< 100) and opened with a 5 × 5 kernel gives a wall mask with
  **IoU 0.89** against the vector mask (false positives: the thick coffee-table frame, a few sofa and lamp parts).
  So the raster path can share the mask → walls code.
- Proximity clustering of the non-wall strokes (0.6 pt buffer) separates sofas (6.31 × 2.41 ft, 2.40 × 6.32 ft), the
  coffee table (3.8 ft square, nested frame), a round 1.51 ft object, the dining set; beds and the kitchen counter
  line touch wall outlines and merge with them until the wall outline strokes are removed first.
- The current pipeline stops real01 at `needs_review` ("no plan title found"), and even with a title it would find
  no walls (line-width buckets 0.5/0.35/0.25 pt), no scale (needs 3 agreeing dimensions; real01 has 2, in feet), and
  English labels map to room type `other`.
- DWG: LibreDWG tag `0.14` (commit d9468ae948b8f07a08efa756c19f8916052358c0, 27 Jun 2026; there is **no 0.14.1**,
  which is why the M4 download failed) builds from git with `cmake -G Ninja` in 2 min 18 s on 4 cores. `dwg2dxf`
  reproduces the AutoCAD reference DXFs of LibreDWG's own test data (R14–R2018: same layers, blocks, inserts; one
  ACAD_TABLE and one ARC_DIMENSION dropped), and DWG copies of synthetic-01 and synthetic-04 (written as AC1015 with
  `$DWGCODEPAGE=ANSI_1254`) give a `building.json` with **0 differences** from the DXF runs. ezdwg 0.12.12 is not
  usable as a fallback (units always metres, inserts and dimensions exploded). GitHub release pages are blocked for
  this session; `git clone` through the git proxy works.
- Hugging Face API (from the session): `allenai/objaverse` (ODC-By, `lvis-annotations.json.gz` 0.9 MB,
  `object-paths.json.gz` 19.8 MB, 160 metadata shards × 3.6 MB; per-object licences in the metadata) — LFS downloads
  are blocked here, so the library survey runs on the pod. Detectors: `google/owlv2-base-patch16-ensemble`
  (Apache-2.0, rev cfd3195ba4ea9592eec887ded089f4c08eff231d), `IDEA-Research/grounding-dino-base` (Apache-2.0, rev
  12bdfa3120f3e7ec7b434d90674b3396eccf88eb), `microsoft/Florence-2-large` (MIT).
- Six read-only mappers (ingest, recognition, look/library/cameras, check/realism, orchestrator, DWG) listed the
  hook points and the tests that pin current behaviour; the section references below use them.

Scope (areas, §1.5 owns the files):
1. **G** – generic plan core and the CAD-PDF adapter (real01): units in feet/inches and metres, English plan
   vocabulary, hatch/fill/outline walls, openings from wall gaps and symbols, open-plan rooms, plot and exterior,
   furniture clusters, stairs, kitchen counters (§2).
2. **Y** – AI typing of unnamed furniture clusters and raster texts: crops, two VLM passes, size tables (§3).
3. **S** – raster adapter: scans, phone photos, raster-only PDF pages (§4).
4. **D** – DWG through LibreDWG 0.14 and a generic DXF adapter for files without the synthetic layer names (§5).
5. **L** – AgX Punchy, one view for rooms without furniture, style-filtered library, new parametric types,
   stairs and open-plan geometry in Blender (§6).
6. **O** – a larger CC0 / CC-BY library from Objaverse, surveyed and judged on the pod (§7).
7. **V** – detection of objects the polish adds, insertion measured every run; realism protocol v2 (§8).
8. **R** – orchestrator stages, 96 GB GPU tier, time rule, report, copy rules, runner (§9).
9. Pods: recognition + library + calibration, then full runs of real01 and every synthetic project with the new look,
   then the realism A/B (§10).

Out of scope: TRELLIS.2 or any image-to-3D generation (no documented provenance of the shape; plan §4.8 keeps it as a
later fallback), angled or curved walls (warning; `needs_review` only when they are part of the outer loop), upper
floors that the documents do not draw (real01 draws a stair but no first floor: the stair is built up to the ceiling,
§6.4), exterior and landscape renders (the plot wall, parking and garden are recorded in `site`, not built), paper
space and layouts of DWG/DXF files, sections and elevations, SketchUp/Revit/IFC inputs, OCR of hand-written notes.

## 0. Decisions (changes to `docs/plan.md` and earlier specs)

| Before | Now | Why |
|---|---|---|
| Plan pages need a Turkish title (`KAT PLANI`, …), else class `other` (skipped) | a vector or raster page with no title but with **room-name labels** from the English or Turkish vocabulary and a wall structure is a `floor_plan` (confidence 0.6, evidence = the labels); a project with exactly one plan page and no level title gets level `L0` "Ground floor" as an **assumed** value (warning, report) | real01 has no title; a missing level title is not geometry, so it is assumed and listed, not a stop. Missing scale or an open outline still stop the project |
| Lengths are metres (`4,50`), areas m² | one parser for metres, centimetres, millimetres, feet and inches (`50'`, `9' 3"`, `4'-9"`, `11'3"`, `10 ft`, `3.5 m`, `350 cm`), size pairs (`11' x 10'`) and areas (`110 sq ft`, `24,50 m²`); a page's unit system is the majority of its parsed texts; reports show imperial projects in feet-inches with metres | real01 is imperial; the Indian and US market draws in feet |
| Scale: a scale note, or ≥ 3 dimension texts agreeing within 1 % | generic pages: a scale note; or ≥ 3 dimensions within 1 %; or **2 dimensions within 0.5 %** corroborated by ≥ 2 room-size labels within 5 % (confidence 0.85); or 1 dimension corroborated by ≥ 3 room-size labels within 5 % (confidence 0.7, warning). Size labels alone never give a scale (`needs_review`) | real01 has two dimensions; size labels are rounded clear sizes, good as a check, too weak as the only source |
| Walls = closed 0.5 pt rectangles (PDF) or the `DUVAR` layer (DXF) | walls from a **wall mask**: dense hatch groups, dark fills, or closed thin outline polygons, rasterised at 10 mm/px, decomposed into rectangles (`WallItem`); the old line-width and layer paths stay first for the synthetic conventions | real plans hatch or fill walls; the same mask code serves scans and photos |
| Room faces = holes of the wall union; one label per face | wall runs with gaps are one wall with openings (doors, windows, **doorless openings**); free wall ends get **virtual separators** (end-to-wall ≤ 2.4 m, end-to-end ≤ 2.4 m) only when a face would otherwise hold two room names or a stair; labels are merged across lines (`Bath+` / `Toilet`) and the size line is attached to its name | real01 is open plan: drawing, dining, lobby and stair hall share one wall-bounded area |
| Everything inside the outer wall loop is the building | wall components that enclose the house but touch no indoor room (only exterior labels such as Parking, Garden, Lawn, or none) are the **plot**: `site.boundary_walls`, `site.areas`, `site.decor` in the building JSON, not built in 3D | real01's compound wall would otherwise become the outline and the yard a room |
| Furniture types from block names (DXF) or `unknown` (PDF) | **clusters** of non-wall strokes become footprints from the vector geometry; stairs and kitchen counters are typed by deterministic rules; other types come from **two VLM passes (Qwen3-VL-8B, GLM-4.6V-Flash) that must agree** and match the type's size range; otherwise `unknown` + `unverified` with both candidates; a block name with a known keyword types the piece without AI | CLAUDE.md: footprint clear, type unclear → keep the footprint, mark unverified |
| Evidence methods `vector`, `ocr`, `ai`, `derived` | + `raster` (deterministic image processing of a scan/photo) | trust order vector > raster/ocr > ai; the old truth used `ai` for raster walls, wrongly |
| Room types: living, bedroom, kitchen, bathroom, wc, hall, balcony, storage, other, unknown | + `dining`, `prayer` (pooja room; never furnished by AI, decor off) | real01 Dining, Pooja |
| Furniture types (24) | + `stair` (fixed equipment, built like walls), `side_table`, `floor_lamp`, `plant` | real01 stair and the round object near the sofa |
| Raster pages: class `other`, skipped | scans, phone photos and raster-only PDF pages go through the raster adapter (§4); raster texts come from two VLM passes cross-checked with Tesseract; a raster page of a level that also has a vector or DXF page is **evidence only** (matches add evidence, counts are compared, no element is added from it) | user decision 9; prefer DWG > vector PDF > scan > photo |
| DWG: LibreDWG 0.14.1 (does not exist), then ezdwg; not on PATH in full runs | LibreDWG **0.14** (tag pinned to d9468ae) built with cmake/ninja on the pod (cached on the volume) and optionally in the session; `WENART_LIBREDWG_BIN`; the converter version is part of the pipeline fingerprint; no ezdwg fallback (conversion failure → `needs_review`) | user decision 9; measured above |
| DXF: synthetic layer and block names only | a **generic DXF adapter** (any layer names; HATCH, INSERT names, DIMENSION measurements, `$INSUNITS` including inches and feet) feeds the same generic core when the synthetic layers are absent | a real DWG will not use `DUVAR`/`KAPI` |
| Default look AgX, look `None` | **`AgX - Punchy`** (`RENDER_CODE_VERSION = "m7.1"`, look and view transform in the render key); the A/B `look_alt` set compares Punchy (A) with `None` (B) | user decision 6 |
| Rooms get 1–3 views by area | a room with **no furniture after the layout gets 1 view**; a room without furniture and < 2.5 m² gets **no own view** (listed) | user decision 8; real01 Pooja 1.8 m², Store 1.9 m² |
| Any library model whose box fits | library models carry `styles` (style families or `neutral`) and beds `has_mattress`; the fit takes a library model only when its styles contain the project's style family or `neutral`, else the parametric mesh; beds without a mattress are dropped | user decision 7 |
| Poly Haven CC0 only | + Objaverse objects with licence **CC0 or CC-BY 4.0** (no NC, no ND, no SA), judged by two VLMs on Blender thumbnails; CC-BY credits in the final report and in `results/final/<p>/ATTRIBUTION.md` | user decision 7 |
| Insertion ("added by polish") practically never confirmed (GLM returns no extras; controls not asked in full runs) | an **open-vocabulary detector (OWLv2)** compares Cycles and polished images; a detected added object confirmed by the detector's strong score or by either VLM rejects the polished image; insertion controls are asked in every full run and calibrate the detector | user decision 3 (vision check stays advisory for absolute flags) |
| Realism: 4 aspects in one call | **one aspect per call**, both orders, the order of the two images also alternated inside the question text and the answer enum; new answer files (M6 answers kept) | user decision 5 |
| vLLM ≥ 40 GB: 16k context, 4 sequences | + a ≥ 80 GB tier: 32k context, 8 sequences (RTX PRO 6000, 96 GB) | faster checks on the new default GPU |
| Time rule measured on the PRO 4500 | + a per-GPU speed factor measured in pod A; recognition and symbol calls counted | the runner now picks the RTX PRO 6000 |

## 1. Shared contracts (read before any area)

### 1.1 Units (`wenart/units.py`, new, stdlib only; owner G)

```python
@dataclass(frozen=True)
class Length:
    metres: float
    system: str          # "imperial" | "metric"
    text: str            # as printed
    precision_m: float   # half the printed resolution: 1 in → 0.0127, 1 cm → 0.005, "4,50" → 0.005
def parse_length(text, default_system=None) -> Optional[Length]
def parse_size_pair(text, default_system=None) -> Optional[tuple[Length, Length]]   # "11' x 10'", "3,20 x 4,10", "14'-0\" X 12'-0\""
def parse_area(text) -> Optional[tuple[float, str]]                                  # (m², "imperial"|"metric")
def format_length(metres, system) -> str      # imperial: 11' 3" (nearest inch); metric: 3,40 m (existing style)
def format_area(m2, system) -> str            # imperial: 110 sq ft; metric: 24,50 m²
FT = 0.3048; INCH = 0.0254; SQFT = 0.09290304
```
- Accepted marks: `'` `’` `′` for feet, `"` `”` `″` `''` for inches, `ft`, `feet`, `in`, `inch`; `-` or space between
  feet and inches; `x`, `X`, `×`, `*` between pair members. Bare numbers: comma decimal → metric metres (existing
  rule); a bare integer with `default_system="imperial"` is feet only when the page's other texts are imperial;
  `mm`/`cm`/`m` suffixes as today. `parse_number` in `wenart/ingest/model.py` and `_AREA_RE` in `building.py` call
  this module (existing metric behaviour and tests unchanged).
- A page's `unit_system` = majority of its parsed lengths (dimension texts first, then size labels), ties → metric.
  Stored in `LevelExtraction.units_system` and `documents[].unit_system`; the building gets
  `project.unit_system` (the master pages' system).

### 1.2 Generic page model (`wenart/ingest/generic/model.py`, new; owner G)

Every adapter (CAD PDF, generic DXF, raster) produces one `GenericPage`; one core (`wenart/ingest/generic/core.py`)
turns it into a `LevelExtraction` (the existing contract, `model.py:113`), so rooms, links, cross-checks, the
building JSON and the report stay shared.

```python
@dataclass
class Stroke:            # a drawn line, polyline, arc or circle, in page units (pt / DXF units / px), y up
    id: str              # "path:123", "ent:1A2B", "seg:45" (raster)
    kind: str            # "line" | "polyline" | "arc" | "circle" | "curve"
    pts: list[tuple[float, float]]          # flattened, ≥ 2 points (arc/circle sampled ≤ 2° per step)
    closed: bool
    colour: Optional[tuple[float, float, float]]   # stroke RGB 0..1, None = unknown / black raster
    fill: Optional[tuple[float, float, float]]     # fill RGB when filled
    width: float                                    # line width in page units (0 = hairline)
    layer: Optional[str] = None; block: Optional[str] = None   # DXF only (block = innermost INSERT name chain "A/B")
    arc: Optional[dict] = None                      # {"center", "radius", "start_deg", "end_deg"} when known exactly
    source: str = "vector"                          # "vector" | "raster"
@dataclass
class TextRun:           # one line of text
    id: str; text: str; box: tuple[float, float, float, float]   # page units, y up
    height: float; rotation_deg: float
    source: str          # "vector" | "ocr" | "ai"
    evidence: list[dict] # building.evidence objects (ocr/ai: model, pass, confidence)
@dataclass
class DimensionPrim:     # a dimension known as such (DXF DIMENSION entity; raster/PDF ones are found by the core)
    id: str; p1: tuple; p2: tuple; measured_units: float; text: Optional[str]
@dataclass
class GenericPage:
    file: str; page: int; source_kind: str           # "cad_pdf" | "dxf" | "raster_scan" | "raster_photo"
    units: str                                        # "pt" | "dxf" | "px"
    units_to_m: Optional[float]                       # known a priori (DXF $INSUNITS); None = must be resolved
    size: tuple[float, float]
    strokes: list[Stroke]; texts: list[TextRun]; dimensions: list[DimensionPrim]
    wall_mask: Optional["MaskLayer"] = None           # raster pages give the mask directly
    wall_hint_layers: tuple[str, ...] = ()            # DXF layer names that look like walls (WALL, A-WALL, DUVAR, …)
    to_original: Optional[list] = None                # 3×3 page-units → original pixels (photos), for evidence boxes
@dataclass
class MaskLayer:
    mask: "np.ndarray"; origin: tuple[float, float]; px: float   # bool [rows, cols], page-units of one pixel, y up
```
- `core.extract(page: GenericPage, level_id, answers=None) -> LevelExtraction` runs, in this order: texts → unit
  system → dimensions → scale (§2.3) → walls (§2.4) → plot and building (§2.5) → openings (§2.6) → labels (§2.7)
  → furniture candidates (§2.8) → apply AI answers if given (§3). With no scale it returns early exactly like
  `pdf_extract.extract_from_objects` (the pipeline then stops with `needs_review`).
- `LevelExtraction` gets new optional fields (defaults keep every existing caller working): `units_system`,
  `site` (§1.3), `separators` (virtual separators, §2.7), `candidates` (furniture candidates not yet typed, §2.8),
  `stair` items go into `furniture` with type `stair`, `wall_mask_png` (path of the debug mask), `source_kind`.
- Frame: as today (metres, X right, Y up, origin at the min corner of the **building** walls — plot walls do not move
  the origin).

### 1.3 Building JSON additions (`wenart/schema/building.schema.json`, `wenart/building.py`; owner G)

- `evidence.method` enum + `raster`. `page.scale.method` enum + `room_size_label` (corroboration only; never the
  sole source).
- `rooms[].room_type` enum + `dining`, `prayer`. `rooms[].label_size` (optional): `{"text", "width_m", "length_m",
  "measured": [w, l], "status": "ok|conflict|unchecked"}`.
- `furniture[].type` enum + `stair`, `side_table`, `floor_lamp`, `plant`. New optional fields:
  `type_candidates` (list of `{type, model, pass, confidence}`), `type_method` (`block_name` | `rule` | `ai_two_pass`
  | `none`), `stair` (`{"flights": [{"start", "end", "width", "treads"}], "tread_m", "riser_m_assumed": 0.17}`),
  `counter_run` (`{"wall_id", "polyline_entity"}`).
- `openings[].kind` stays `door | window | opening`; new optional `virtual: true` with `line: [[x,y],[x,y]]` and
  `wall_id: null` for virtual separators (`kind: "opening"`), `height` and `sill` with `assumed: true` where
  defaulted (door 2.10, doorless 2.10, window sill 0.90, window height 1.20).
- `site` (optional top-level object): `{"boundary_walls": [wall-like dicts, id prefix `sw_`], "areas": [{"id":
  "sa_L0_parking", "label", "label_size", "polygon": null|[...], "evidence"}], "decor": [{"id", "kind":
  "plant|tree|car|other", "center", "size", "evidence"}], "openings": [...]}` — recorded, reported, never built.
- `project.unit_system`, `documents[].unit_system`, `documents[].source_kind`.
- `warnings` stays free text; the new `conflicts[].kind` values: `label_size_mismatch`, `symbol_type_disagreement`,
  `raster_count_mismatch`, `scale_disagreement`.
- `ROOM_TYPE_PRIORITY` gets `dining` and `prayer` (after `storage`, before `balcony`); the English keywords
  (§2.7.2) are added to `_ROOM_TYPE_KEYWORDS`. `tests/test_building.py:113` is updated with the new tuple.

### 1.4 Recognition requests and answers (`wenart/recognition/answers.py`, new; owner Y)

The pipeline is CPU-only and runs before any VLM server. It writes questions; a GPU stage answers them; the pipeline
re-runs with the answers.

- `<out>/recognition/requests.json`: `{"schema_version": "0.1", "kind": "recognition_requests", "project", "items":
  [{"key", "task": "symbol_type|page_texts|room_label", "page", "images": ["crops/<key>_ctx.png",
  "crops/<key>_iso.png"], "context": {...}, "input_sha256"}]}` (paths relative to `<out>/recognition/`).
- `<out>/recognition/answers_<slug>.json` (`slug` = `check.yaml models.<key>.slug`): the M5 `AnswerStore` pattern
  (`vision_check/calls.py:312`): an answer is reused when key and `input_sha256` match; schema-valid or recorded as an
  error; temperature 0, seed 0, structured outputs.
- CLI: `python -m wenart.recognition.answers ask <out>/recognition --model-key qwen|glm --server URL --workers N
  [--deadline T]` (exit 0 all answered, 3 deadline, 2 server error) and `python -m wenart.recognition.answers
  status <out>/recognition` (counts per model).
- Pipeline: `python -m wenart.ingest.pipeline <proj> --out <out> [--answers <out>/recognition]`. Exit codes: 0 ok,
  1 needs_review, **4 = questions written, answers missing** (building written with the current state: furniture
  `unknown`/`unverified`, raster labels from Tesseract only). A run with `--answers` and both answer files complete
  never exits 4. Without `--answers` a project that has requests exits 4 (the scheduler then asks, §9.1); a
  CPU-only user may pass `--no-ai` to get exit 0/1 with everything AI would decide left `unverified`.

### 1.5a Internal interfaces of the generic core (G1 text, G2 geometry, G3 integration)

All core functions work in **page metres**: page units × `units_to_m`, y up, no offset (so every function can run
before the building origin is known). `core.extract` shifts everything to the building frame at the end
(`transform_to_building = [s, 0, -ox, 0, s, -oy]`, `(ox, oy)` = min corner of the building walls).

```python
# generic/labels.py (G1)
def room_name_runs(texts: list[TextRun]) -> list[TextRun]                  # runs whose text has a room-name keyword
def merge_label_blocks(texts, units_to_m) -> list["LabelBlock"]             # §2.7.2: name + optional size / area line
@dataclass class LabelBlock: name: str; name_runs: list[TextRun]; size_text: Optional[str]; area_text: Optional[str]
                             anchor: tuple[float, float]; room_type: str; exterior: bool; evidence: list[dict]
# generic/scale.py (G1)
def find_dimensions(page: GenericPage) -> list["DimCandidate"]              # §2.3, page units
def provisional_scale(page, dims) -> Optional[dict]                         # schema scale dict or None (+ reasons)
def confirm_scale(scale, dims, label_blocks, faces_m) -> tuple[Optional[dict], list[dict], list[str]]  # scale, conflicts, warnings
# generic/walls.py (G2)
def wall_primitives(page: GenericPage, units_to_m: float) -> list["WallPrim"]     # hatch groups, fills, outlines, layer hints, raster mask
def wall_mask(page, prims, units_to_m, px_m=0.01) -> MaskLayer                     # in page metres
def walls_from_mask(mask: MaskLayer, file_rel: str, page_no: int) -> tuple[list[WallItem], dict]  # rects (page metres) + stats
# generic/openings.py (G2)
def runs_and_openings(walls, strokes_m, file_rel, page_no) -> tuple[list[WallItem], list[OpeningItem], list[dict]]  # merged runs, openings, gap log
# generic/topology.py (G2)
def split_plot(walls, openings, label_blocks) -> tuple[list[WallItem], dict, list[str]]   # building walls, site dict, warnings
def separators(walls, openings, label_blocks, stairs) -> tuple[list[OpeningItem], list[dict]]  # kept, considered
# generic/symbols.py (G2)
def candidates(strokes_m, walls, openings, texts_m, dims, outline, rooms) -> tuple[list[FurnitureItem], list[dict], list[dict]]
                                                                             # typed pieces (rules), AI candidates, site decor
# generic/core.py (G3)
def extract(page: GenericPage, level_id: str, file_rel: str, answers: Optional[dict] = None) -> LevelExtraction
```
`strokes_m` / `texts_m` are the page's strokes and texts converted to page metres by `core` (one helper,
`core.to_metres(page, units_to_m)`). G1 and G2 write unit tests against hand-made `GenericPage`s; G3 wires them and
owns the real01 acceptance.

### 1.5 Ownership (parallel implementation, wave 1 and wave 2)

| Area | Wave | Owns |
|---|---|---|
| G generic core + CAD PDF | 1 | `wenart/units.py`, `wenart/ingest/generic/*` (new: `model.py`, `core.py`, `walls.py`, `openings.py`, `topology.py`, `symbols.py`, `scale.py`, `labels.py`), `wenart/ingest/cad_pdf.py` (new adapter), `wenart/ingest/{classify,pdf_extract,model,rooms,pipeline,debug_image}.py`, `wenart/building.py`, `wenart/schema/building.schema.json`, `docs/examples/building.example.json`, `tests/fixtures/real01_reference.yaml` (new), `tests/test_units.py`, `tests/test_generic_*.py`, `tests/test_cad_pdf.py`, `tests/test_real01.py` (new), `tests/test_{classify,pdf_extract,rooms,pipeline,building}.py` |
| Y AI typing | 1 | `wenart/recognition/{answers,symbols,page_texts,prompts,schemas,vlm_client}.py`, `wenart/recognition/size_table.yaml` (new), `tests/test_recognition_answers.py`, `tests/test_symbols.py`, `tests/gpu/test_recognition.py` |
| D DWG + generic DXF | 1 | `wenart/ingest/dwg.py`, `wenart/ingest/dxf_generic.py` (new adapter), `wenart/ingest/dxf_extract.py` (dispatch only), `wenart/synthetic/*` (synthetic-06), `projects/synthetic-06/` (generated), `docs/synthetic.md`, `scripts/pod_setup_recognition.sh` (libredwg part), `scripts/pod_setup.sh` (PATH/env only), `scripts/cloud-setup.sh`, `wenart/intake.py` (DWG rule texts), `docs/intake.md`, `tests/test_dwg.py` (new), `tests/test_dxf_generic.py` (new), `tests/test_synthetic.py`, `tests/test_intake.py`, `tests/test_recognition_cpu.py` (libredwg pins) |
| L look/cameras/library/Blender | 1 | `wenart/blender/*`, `wenart/style/{vocabulary,profile}.py`, `wenart/defaults.yaml` (style block), `wenart/furniture/{catalog.py,catalog.json,fit.py,schemas.py,layout.py,decor.py,placer.py}`, `wenart/assets/{fetch,models}.py` (licence gates), `tests/test_blender_*.py`, `tests/test_camsearch.py`, `tests/test_look_m6.py`, `tests/test_furniture_fit.py`, `tests/test_style.py`, `tests/test_layout.py`, `tests/test_placer.py`, `tests/test_decor.py`, `tests/test_assets.py`, `tests/test_models_assets.py`, `tests/gpu/test_render.py`, `tests/gpu/test_look_m6.py`, `tests/gpu/test_furnish.py` |
| O Objaverse library | 1 | `wenart/assets/objaverse.py` (new), `wenart/assets/objaverse.yaml` (new), `scripts/jobs/library.sh` (new), `tests/test_objaverse.py` (new), `tests/gpu/test_library.py` (new); catalog entries are merged by L's `catalog.py` loader from `wenart/furniture/catalog_objaverse.json` (O writes it, L reads it) |
| V check + realism | 1 | `wenart/vision_check/*`, `wenart/gate/{detect.py (new), models.yaml, models.py}`, `tests/test_vision_check_*.py`, `tests/test_realism_ab.py`, `tests/test_detect.py` (new), `tests/test_m5_config.py` (pins that change), `tests/gpu/test_check.py`, `tests/gpu/test_realism.py` |
| R run | 2 | `wenart/run/*`, `scripts/jobs/full.sh`, `scripts/gpu_run.py`, `scripts/pod_entry.sh`, `scripts/pod_setup_polish.sh` (parts), `wenart/report/*`, `tests/test_run_*.py`, `tests/test_full_job.py`, `tests/test_report.py`, `tests/test_gpu_run.py`, `tests/fakes/*`, `tests/gpu/test_full_run.py` |
| S raster | 2 | `wenart/ingest/raster.py` (new adapter), `wenart/ingest/rectify.py` (new), `wenart/synthetic/raster.py` (real01 raster fixtures), `tests/fixtures/real01_raster/` (generated, small), `tests/test_raster.py` (new), `tests/test_rectify.py` (new) |

Wave 2 starts when wave 1 is integrated (S builds on G's core; R wires every new CLI). Interfaces between areas are
§1.1–§1.4, §3.4, §6.6, §7.4, §8.3. A change to a shared contract goes through the integrator. Files outside the
table are changed only by the integrator (`docs/*`, `CLAUDE.md`, `pyproject.toml`).

## 2. Area G – generic plan core and the CAD PDF adapter

### 2.1 Page classification (`classify.py`)

- `_classify_pdf` keeps the title rule first. When no title is found and the page is vector: run
  `generic.labels.room_name_runs(texts)` (§2.7.2); with ≥ 2 room-name runs **and** ≥ 1 wall candidate group
  (§2.4, cheap test: a hatch group or a dark fill or ≥ 4 closed thin polygons), the page is `floor_plan`,
  `confidence 0.6`, `evidence` = the label runs, `skip_reason None`, `classifier: "generic_labels"`. Otherwise
  unchanged (`other`). `classify_texts([room label])` keeps returning `other` (`tests/test_classify.py:91`).
- Level: title rule as before; else, if the project has exactly one plan page without a level title →
  `level_id "L0"`, `level_label "Ground floor"`, `level_assumed: true` (warning "level title missing: assumed L0
  Ground floor", report row). Several untitled plan pages → `needs_review` ("cannot order untitled plan pages").
- English level titles are recognised: `GROUND FLOOR`, `FIRST FLOOR`, `SECOND FLOOR`, `BASEMENT`, `n-th FLOOR`,
  `FLOOR PLAN`, `FURNITURE (LAYOUT) PLAN` (class keywords), case-insensitive.

### 2.2 CAD PDF adapter (`wenart/ingest/cad_pdf.py`)

`cad_pdf.read_page(path, page) -> GenericPage` with `pdfplumber` (already used): every line, curve and rect
becomes a `Stroke` with `colour = stroking_color`, `fill = non_stroking_color if fill`, `width = linewidth`
(normalising pdfplumber's colour forms: gray floats, RGB tuples, CMYK → RGB), `pts` in PDF points with y up (pdfplumber
`top` is y-down: convert once here, and test it). Beziers are flattened (≤ 0.25 pt chord error) and recognised as
arcs when they fit a circle within 1 % of the radius (`arc` filled in). Texts: `merge_chars` runs (`pdf_extract`)
with box, height and rotation. Zero-length strokes (dots) are kept as `kind "line"` with two equal points.
`pipeline.py` dispatches a `floor_plan`/`furniture_plan` PDF page whose `classifier == "generic_labels"` (or whose
title page has no 0.5 pt wall rectangles) to `core.extract(cad_pdf.read_page(...))`; synthetic PDFs keep
`extract_pdf_page` (their tests stay green).

### 2.3 Dimensions and scale (`generic/scale.py`)

- **Dimension candidates**: a text run that parses as a single length (§1.1), plus a straight stroke (or two collinear
  strokes interrupted by the text) parallel to the text baseline within `2.5 × text height`, whose ends carry end
  marks — filled triangles (arrowheads, tip = end), short strokes at 30–60° (ticks, centre = end), dots, or
  perpendicular extension lines. Measured length = distance between the two end points. Two dimension candidates
  that share a line are both kept. DXF `DimensionPrim` are used as given (measured from the entity).
- `ratio_i = printed_m / measured_units`. **Rules** (first that holds wins): scale note → `pdf_scale_text`
  (unchanged); ≥ 3 ratios agree within 1 % and are the majority → `dimension_text` 0.9 (unchanged); exactly 2
  agree within 0.5 % **and** ≥ 2 room-size labels (§2.7.3) agree with that ratio within 5 % → `dimension_text`
  0.85; 1 dimension and ≥ 3 room-size labels within 5 % → `dimension_text` 0.7 + warning "scale from one
  dimension, corroborated by N room sizes". Anything else → no scale → `needs_review` ("no scale: …" with the
  candidates listed). Every dimension that disagrees with the chosen ratio by > 1 % → `scale_disagreement`
  conflict. Room-size corroboration needs the rooms, so `core.extract` computes a provisional scale from the
  dimensions, derives rooms, then confirms or rejects it (a rejected provisional scale → `needs_review`).
- real01: `50'` ↔ 621.8 pt, `30'` ↔ 373.1 pt (arrowhead tips); ratio 0.024512 m/pt both; corroborated by the 8
  size labels (§2.10).

### 2.4 Walls (`generic/walls.py`)

1. **Wall primitives** (any of, in this order of confidence):
   - *hatch groups*: ≥ 20 straight strokes of one colour, one direction (± 1°) and length ≤ 0.6 m, whose
     perpendicular offsets form a regular comb (median step ≤ 25 mm at the provisional scale; real01: 0.12 pt ≈ 3 mm)
     → method `vector`, confidence 0.95, entity `hatch:<group>`;
   - *dark fills*: filled closed strokes with luminance ≤ 0.35 → 0.9, entity `fill:<id>`;
   - *outline walls*: closed stroked polygons (or rectangles) of 4–12 vertices whose minimum width is 0.05–0.60 m
     and length ≥ 0.4 m and that contain no other stroke of another cluster → 0.8, entity `outline:<id>`;
   - DXF: HATCH / SOLID / closed polylines on a wall-hint layer → 0.95; raster: the given mask → `raster`, 0.85.
2. Rasterise the primitives into a mask at **10 mm/px** (polygon fill; hatch lines drawn 2 px wide, then a 3 × 3
   closing); drop components < 0.02 m² or not elongated (both bounding sides < 0.25 m) unless they touch a wall.
3. **Decompose** into axis-aligned rectangles in the drawing's dominant orientation (the strongest pair of
   perpendicular stroke directions; real01 0°/90°): maximal horizontal and vertical strips whose cross-section is
   constant within 1 px; at T and L junctions the through-wall keeps the junction square, the other wall ends at its
   face (as the synthetic DXF draws them). Thickness rounded to 5 mm; centre line from the strip. The union of the
   rectangles must reproduce the mask with IoU ≥ 0.97 (else warning with the missed area).
4. Thickness classes (clusters within 15 mm) are reported (real01 ≈ 0.165 m and ≈ 0.235 m expected). Walls that
   are not axis-aligned (> 3°): warning `angled wall not modelled`; `needs_review` only when such a wall is needed
   to close the outer loop.

### 2.5 Plot and building (`generic/topology.py`)

- Components of the wall mask after bridging openings (§2.6). The **building** is the union of the components whose
  faces hold at least one indoor room-name label (§2.7.2). A component that encloses the building, whose faces
  hold only exterior labels (parking, car porch, porch, garden, lawn, sit out, setback, otla, court, drive, gate) or
  none, and that does not touch a building wall (gap ≥ 0.3 m) → **plot**: its walls go to `site.boundary_walls`
  (`sw_L0_001…`, method vector), its labels to `site.areas` (with `label_size`; the polygon is `null` when the area
  is not closed, as for real01's parking), clusters outside the building outline to `site.decor` (plants: green
  fills or circles with radial strokes → `plant`; everything else `other`). The origin of the building frame is the
  min corner of the building walls (not the plot).
- The **outer loop** = the exterior boundary of the building walls with openings bridged; it must close
  (`needs_review` otherwise, unchanged rule). Exterior walls = walls touching it.
- A label outside both the building and the plot (e.g. the `30'` dimension text before it is consumed, notes) is
  ignored with a warning only if it is not a room-name; an unplaced room-name label is a warning plus the label in
  the report (not `needs_review`, unlike the synthetic rule, because exterior labels are expected on real plans).

### 2.6 Openings (`generic/openings.py`)

- **Wall runs**: rectangles on the same axis line (centre-line offset ≤ 20 mm, thickness ± 30 mm) form a run.
  Between consecutive pieces of a run a **gap** of width g:
  - g < 0.25 m → the pieces are merged (warning `small wall gap closed`);
  - 0.25 m ≤ g ≤ 3.0 m → an **opening**; the run becomes **one** `WallItem` (start of the first piece to the end of
    the last, thickness = the length-weighted median) and the gap an `OpeningItem` on it;
  - g > 3.0 m → two walls (the space between is open; topology §2.7 decides).
- **What is in the gap** (strokes within the gap rectangle grown by 0.35 m on both wall faces):
  - *door*: an arc whose centre is within 0.08 m of a gap end (the hinge) with radius = g ± 12 % and sweep 60–100°
    (single leaf), or two arcs hinged at both ends with radius = g/2 ± 12 % (double); the leaf = a straight stroke
    from the hinge of length ≈ radius (optional). `swing_point` = arc midpoint; swing side = the face the arc is on.
    Evidence: the arc and leaf stroke ids; confidence 0.95 (arc + leaf) / 0.85 (arc only).
  - *window*: ≥ 2 straight strokes parallel to the wall axis inside the wall band (between the faces ± 20 mm)
    spanning ≥ 80 % of g → window; sill 0.90 m and height 1.20 m `assumed`. Confidence 0.9.
  - *doorless opening*: nothing inside the band and no arc → `kind "opening"`, height 2.10 m `assumed`, confidence
    0.8 (an empty gap is geometry, its height is the assumption).
  - anything else (e.g. a sliding-door rectangle pair, a symbol the rules do not know) → `kind "opening"`,
    `status unverified`, `type_raw "unclassified gap content"`, the strokes listed.
- **Openings in continuous walls** (synthetic convention, raster double-line walls): an arc hinged on a wall face with
  radius 0.6–1.2 m and a leaf → door cut into that wall; ≥ 3 parallel strokes inside a wall band over ≥ 0.4 m →
  window. The existing `pdf_extract._door_from_arc` and `_windows_from_lines` rules are moved into this module and
  reused (their tests stay).
- Each opening is linked to its wall as today (`_opening_dict`); doors keep the swing probe.

### 2.7 Rooms (`generic/topology.py`, `generic/labels.py`, `rooms.py`)

#### 2.7.1 Faces and virtual separators
- Faces = holes of the building wall union (openings are part of their wall, so rooms close through doors, windows
  and doorless gaps, as today). `rooms.derive_rooms` gains an argument `union=None` (a ready geometry) and
  `separators=()` (lines that split faces); the old call keeps working.
- **Free wall ends**: an end of a wall with no other wall within 50 mm of its end face.
- **Separator candidates** (method `derived`, evidence = the wall ids):
  - *end-to-wall*: from a free end, along the wall axis, to the first wall face hit within 2.4 m;
  - *end-to-end*: two free ends of parallel walls whose end faces lie within 0.20 m of one line perpendicular to
    the walls and whose distance is ≤ 2.4 m → the segment between them.
- A candidate is **kept** only if, after splitting, a face that held ≥ 2 room-name labels has fewer (each name gets
  its own face), or it separates a stair (§2.8) from a labelled face. Kept separators become openings with
  `kind "opening"`, `virtual true`, `wall_id null`, `line`; dropped ones are listed in the report ("considered, not
  needed"). A face that still holds ≥ 2 names → first name, room `unverified`, conflict (as today).
- Unlabelled faces: type `hall` when the face touches ≥ 2 doors or doorless openings, else `unknown`; label
  `null` (report: "—"); a face that holds a stair gets `hall` and the stair piece. Always `unverified` (type
  derived, not documented).

#### 2.7.2 Labels and vocabulary
- **Label runs** are merged into one label when they are stacked (vertical gap ≤ 0.8 × line height, horizontal
  overlap ≥ 30 %) or a run ends with `+`/`&`/`-` (`Bath+` + `Toilet` → `Bath+ Toilet`). A merged block with a size
  pair (`11' x 10'`) or an area (`110 sq ft`, `12,5 m²`) as its last line → name + `label_size`/area label.
  Anchor point = centre of the name line.
- **Room-name vocabulary** (English, case-insensitive, word start; Turkish list unchanged):

| Type | Keywords |
|---|---|
| living | drawing, living, lounge, family, sitting, hall (alone, only when the face ≥ 9 m² and aspect ≤ 2.5; otherwise `hall`) |
| dining | dining |
| bedroom | bed room, bedroom, master, guest room, kids, children, nursery, br |
| kitchen | kitchen, kit, pantry |
| bathroom | bath, bathroom, shower; `bath` + `toilet` together → bathroom |
| wc | toilet, wc, w.c, powder (only when no bath/shower word) |
| hall | lobby, passage, corridor, foyer, entrance, entry, landing |
| balcony | balcony, terrace, deck, verandah, veranda |
| storage | store, storage, closet, box room |
| prayer | pooja, puja, prayer, mandir |
| other | study, office, utility, laundry, servant, maid, home office |
| *exterior* (plot, not a room) | parking, car porch, porch, garden, lawn, sit out, sit-out, setback, otla, court, courtyard, drive, gate |

#### 2.7.3 Size and area labels
- `label_size`: the pair (w, l) vs the face's **clear** size (minimum-area rectangle of the face polygon, both
  orientations tried): `ok` when both sides are within max(5 %, 0.15 m); `conflict` beyond (conflict
  `label_size_mismatch` listing both sizes; the room becomes `unverified` beyond 10 %); `unchecked` when the face
  is not rectangular (area ratio face / rectangle < 0.9) — then the area w·l is compared with the face area at the
  existing 3 % rule widened to 8 % for imperial rounding.
- Area labels in sq ft use the same `_check_areas` with the unit-aware parser.

### 2.8 Furniture candidates (`generic/symbols.py`)

- **Strokes considered**: inside the building outline, not wall primitives, not wall outlines (≥ 90 % of the stroke
  within 20 mm of the wall mask boundary or inside it), not part of an opening, a dimension, a text box (grown by
  10 %), or a separator.
- **Clusters**: union-find over strokes closer than 20 mm (dots included); then a cluster whose bounding box lies
  ≥ 80 % inside another's is merged into it (pillows into the bed, lamp into the nightstand, the coffee table's inner
  frame). Clusters with both sides < 0.20 m are details (counted, reported, dropped); clusters larger than 4.5 m on a
  side → `unknown`, `unverified` ("too large for one piece").
- **Footprint**: minimum-area rectangle snapped to the dominant orientation when within 3°; `center`, `size`
  [width, depth] (width = the longer side unless a rule fixes the front), `rotation_deg`. Evidence: method
  `vector`, entity = the stroke ids (compressed as ranges), `pixel_box` on the page raster, confidence 0.9.
- **Deterministic types**:
  - *stair*: ≥ 5 parallel strokes of equal length (0.6–1.6 m, ± 5 %) spaced evenly (0.20–0.35 m, ± 10 %) form a
    flight; flights side by side sharing a dividing stroke form a dog-leg; type `stair`, `type_method "rule"`,
    `stair.flights`, `status verified` (the stair is geometry, like a wall). real01: 2 flights in the hall between
    the bedroom wall and the dining wall.
  - *kitchen counter*: an open polyline of ≥ 2 straight segments whose two ends touch walls (≤ 50 mm) and which runs
    parallel to the walls at 0.45–0.75 m → one `kitchen_counter` per straight leg (an L becomes two pieces; the
    corner square belongs to the longer leg), `against_wall`, front away from the wall, `type_method "rule"`,
    `verified` when the room is a kitchen, else `unverified`.
  - *block name* (DXF): a keyword table (`BED`, `SOFA`, `CHAIR`, `TABLE`, `DINING`, `WC`, `TOILET`, `BASIN`,
    `SINK`, `WARDROBE`, `FRIDGE`, `STOVE`/`HOB`, `BATH`, `SHOWER`, `DESK`, `TV`, `PLANT`, `LAMP`, Turkish ones from
    `blocks.py`) → type with `type_method "block_name"`, confidence 0.9, checked against the size table (§3.2).
  - Everything else → a **candidate** for the AI (§3): crops are rendered (§3.1), the piece goes into the building
    as `type "unknown"`, `status "unverified"`, `type_method "none"` until answers exist.
- **Front** (`front_deg`), deterministic candidates first: the side within 0.15 m of a wall is the back (one such side
  only); a bed's head = the side with ≥ 2 small closed shapes (pillows) near it; a chair's back = the side of its
  cluster facing away from the nearest table. The AI front (§3.3) must agree with a unique deterministic candidate, or
  both AI passes must agree when there is none; else `null` (`front_deg` null is allowed and handled by the build).
- **Site decor**: clusters outside the building → `site.decor`.

### 2.9 Report and debug image

- `report.md` gets: `Units: imperial (feet-inches)`, the scale source and its corroboration table (dimension and size
  label ratios), `Site` (plot walls, areas, decor counts), `Separators` (kept and dropped), size-label checks, the
  furniture candidates with type method and candidates, and lengths in the project's unit system (metres in
  brackets).
- The debug image (`debug/<file>_p<n>.png`, 150 dpi) draws: wall mask (semi-transparent), wall centre lines
  coloured by method and confidence, openings (door arcs, windows, doorless dashed), separators (dashed magenta),
  rooms with label and type, furniture footprints coloured by `type_method` (rule green, block_name blue,
  ai_two_pass cyan, none red striped), site elements grey, dimensions used for the scale (orange). `_debug_items`
  uses `evidence.method` instead of the hard-coded `vector`.

### 2.10 real01 reference and acceptance

`tests/fixtures/real01_reference.yaml` is written by hand from the vector data and the 150 dpi render, by two
independent readers whose differences are resolved against the PDF (recorded in the file header). It lists: the
scale (12.436 pt/ft ± 0.2 %), building outline (L-shape, ≈ 42'×24'), the rooms (label, type, label size, approx.
centre in feet from the building origin), doors (5), windows (9 expected, the readers confirm), doorless openings
and separators, furniture (2 `bed_double`, 4 `nightstand`, 1 `table_dining`, 6 `chair`, 2 `sofa`, 1 `table_coffee`,
1 round piece — type left open, 2 `kitchen_counter` legs, 1 `stair` with 2 flights), site (plot wall 50' × 30',
`Parking 11' 3" x 15' 3"`, ≈ 13 plants).

Acceptance (CPU, `tests/test_real01.py`, without AI answers): status `ok`; scale within 0.2 %; every reference room
found with its type and label (8 labelled rooms + the derived stair hall and lobby, if the readers confirm them);
doors and windows recall and precision ≥ 0.9 (centre within 0.15 m, width within 0.10 m); every reference furniture
footprint found (centre within 0.15 m, size within 0.15 m), deterministic types correct; plot recorded, not built;
no element outside the building in `walls`. With fake answers that agree, the AI types are applied; with answers that
disagree, the pieces stay `unknown`/`unverified` with both candidates. On the pod (§10): ≥ 80 % of the AI-typed
pieces get the reference type, and **no** piece is `verified` with a wrong type.

## 3. Area Y – AI typing of unnamed symbols and raster texts

### 3.1 Crops (`recognition/symbols.py`, CPU, called by the core)

Per candidate, two 512 × 512 PNGs rendered with matplotlib/opencv from the strokes (no PDF rasteriser needed):
`<key>_ctx.png` — a square of side max(2.5 m, 1.6 × the larger footprint side) centred on the candidate, walls in
grey, other clusters in light grey, the candidate in black, a red 2 px box around it; `<key>_iso.png` — the candidate
alone, scaled to fill 80 % of the square, with a 1 m scale bar. Keys `sym_<level>_<n>`; `input_sha256` covers both
PNGs, the prompt, the schema and the allowed type list.

### 3.2 Size table (`recognition/size_table.yaml`)

Per type a plausible footprint range in metres (width × depth, either orientation, ± 15 % applied on top), e.g.
`bed_double: [[1.30, 1.90], [1.80, 2.30]]`, `chair: [[0.35, 0.70], [0.35, 0.75]]`, `nightstand: [[0.30, 0.70],
[0.30, 0.60]]`, `table_coffee: [[0.45, 1.50], [0.45, 1.50]]`, `side_table: [[0.30, 0.70], [0.30, 0.70]]`, … for all
furniture types (sources cited in the file: Neufert-style standard sizes; the synthetic block table). The core and
Y both use it; the DXF block-name path checks it too.

### 3.3 Symbol question and the two-pass rule

- Prompt (both models; temperature 0; JSON schema): "Two crops of an architectural floor plan seen from above. The
  red box in the first image (shown alone in the second, with a 1 m bar) marks one drawn object. Which object type is
  it?" Schema: `{"type": enum(furniture types ∪ {"not_furniture"}), "front": enum("top","right","bottom","left",
  "none"), "confidence": number 0..1, "reason": string ≤ 160}`. The allowed list in the prompt is the full type list
  (no room hint, so the room type cannot bias the answer; the room check comes after).
- Pass 1 = Qwen3-VL-8B, pass 2 = GLM-4.6V-Flash (`check.yaml models`; the same pinned revisions).
- **Rule**: type T is accepted (`type_method "ai_two_pass"`, `status verified`, evidence: vector footprint + two
  `ai` entries, confidence = min of the two, capped at 0.9) only when both passes say T **and** the footprint fits
  T's size range. Otherwise `type "unknown"`, `status "unverified"`, `type_candidates` = both answers, conflict
  `symbol_type_disagreement`. Both say `not_furniture` → the cluster is dropped from `furniture` and listed in the
  report ("drawn symbol, not furniture"), evidence kept. A type not allowed in the room (`ALLOWED_TYPES` plus
  `side_table`, `floor_lamp`, `plant` everywhere, `stair` in halls) → kept, `unverified`, warning.
- Front: §2.8. A `stair` or `kitchen_counter` from the rules is never asked.

### 3.4 Raster texts (`recognition/page_texts.py`) – used by S

- Per raster page one request `page_texts` with the rectified page image (≤ 1600 px long side) and, for each room
  face found by the geometry, a request `room_label` with the face crop (face grown by 0.5 m, 768 px).
  - `page_texts` schema: `{"title": str|null, "scale_text": str|null, "dimensions": [{"text", "box"}],
    "unit_system": "metric|imperial|unknown"}` (boxes on the 0–1000 grid, converted to page pixels).
  - `room_label` schema: `{"label": str|null, "size_text": str|null, "area_text": str|null}`.
- **Rule**: a room label is accepted (method `ocr`+`ai` evidence, confidence 0.8) when the two passes give the same
  normalised text (casefold, Turkish-aware, spaces collapsed) **or** one pass equals the Tesseract text read inside
  the face; else the label is `null`, the room `unverified`, both candidates listed. Dimension texts: a raster
  dimension line (S finds it) with a text both passes (or one pass + Tesseract) read the same → a dimension; the
  scale rules of §2.3 apply unchanged.

## 4. Area S – raster adapter (scans, phone photos, raster-only PDF pages)

### 4.1 Input and rectification (`wenart/ingest/rectify.py`, `raster.py`)

- Inputs: `.png`, `.jpg`, `.jpeg`, `.tif`; raster-only PDF pages (no vector paths, an image covering ≥ 50 % of the
  page) are rendered at 200 dpi with `pdftoppm` (`classify._classify_pdf` passes the path).
- Photo (`classify.raster_kind == "photo"`): the page quadrilateral (largest 4-point contour covering ≥ 30 % of
  the image) → homography to a fronto-parallel image whose aspect is the quad's mean side ratio; `to_original` keeps
  the inverse so every `pixel_box` in evidence is in the original photo's pixels. No quad → the page is
  `needs_review` for that level unless another page of the level exists (then evidence only).
- Deskew: the dominant direction of the long dark strokes (Hough on the dark mask), applied as a rotation; ≤ 5°.

### 4.2 Wall mask and strokes

- Dark mask = adaptive threshold (block 51 px, C 10) ∪ Otsu; text boxes (Tesseract `eng+tur`, psm 11) are blanked.
- **Filled walls** (real01 style): opening with a square kernel of `k = max(3, round(0.6 × t_min))` px, where
  `t_min` is the thinnest wall thickness candidate: the lowest mode ≥ 4 px of the distance-transform histogram of the
  dark mask (× 2). Components that are closed thin rings enclosing < 2 m² (the coffee-table frame) or are not
  connected to an elongated component are dropped.
- **Outline walls** (synthetic-02 style: two thin parallel lines, continuous through openings): pairs of long
  parallel line segments (LSD or `HoughLinesP` on the skeleton) at distance 0.07–0.50 m (provisional scale; before the
  scale: 6–40 px) with ≥ 70 % overlap → the band between them filled into the mask.
- The mask goes to `GenericPage.wall_mask` (px units, `px = 1`); the thin-line skeleton becomes `Stroke`s
  (`source "raster"`): straight segments (merged collinear within 1 px) and **arcs** found by a circle fit on
  skeleton chains (RANSAC, radius 0.5–1.3 m at the provisional scale, sweep ≥ 50°). The core (§2.6, §2.8) does
  the rest: openings, furniture clusters (footprints from raster strokes, method `raster`, confidence 0.7).
- Provisional scale: dimension texts (§3.4) + dimension lines; before the answers exist, Tesseract texts only
  (likely too weak: then exit 4 and wait for the answers).

### 4.3 Targets (CPU tests with saved or fake answers; pod with real ones)

| Page | Walls F1 (centre ≤ 0.10 m, thickness ≤ 0.05 m) | Openings recall (kind + centre ≤ 0.20 m) | Rooms with right label | Scale error |
|---|---|---|---|---|
| synthetic-02 scan | ≥ 0.9 | ≥ 0.8 | 5/5 | ≤ 2 % |
| synthetic-02 photo | ≥ 0.8 | ≥ 0.7 | 5/5 | ≤ 3 % |
| real01 scan (generated: 150 dpi, ±1.5° rotation, noise σ 4, blur σ 0.7) | ≥ 0.9 vs the vector result | ≥ 0.8 | ≥ 7/8 | ≤ 2 % |
| real01 photo (generated: as synthetic-02's photo) | ≥ 0.8 | ≥ 0.7 | ≥ 7/8 | ≤ 3 % |

synthetic-02 becomes a normal project (end state `ok` when the targets hold on the pod; its truth `building.json`
evidence methods move from `ai` to `raster` for walls and openings — regenerated, not edited by hand). synthetic-01's
`1_kat_scan.png` becomes evidence for L1 (no new elements; a `raster_count_mismatch` conflict when counts differ).
The real01 raster fixtures live in `tests/fixtures/real01_raster/` (generated by `wenart.synthetic.raster` from
`projects/real01/real01.pdf`, ≤ 1.5 MB each), not as projects.

## 5. Area D – DWG and the generic DXF adapter

### 5.1 LibreDWG
- `pod_setup_recognition.sh` part `libredwg`: `LIBREDWG_TAG=0.14`, `LIBREDWG_COMMIT=d9468ae948b8f07a08efa756c19f8916052358c0`;
  `git clone --depth 1 --branch 0.14` + `git submodule update --init --depth 1 jsmn`, verify `git rev-parse HEAD`,
  `cmake -G Ninja -DCMAKE_BUILD_TYPE=Release -DDISABLE_WERROR=ON -DENABLE_LTO=OFF`, `ninja dwg2dxf dwgread`, install
  into `/workspace/tools/libredwg/bin` with a `VERSION` file (`0.14 d9468ae`); skipped when `VERSION` matches. apt adds
  `cmake ninja-build`. `full.sh` setup asks for the part (≈ 2.5 min the first time, then reused from the volume).
- `scripts/cloud-setup.sh` builds it into `~/.cache/wenart/libredwg` when `git` and `cmake` exist (optional; tests skip
  without it).
- `dwg.py`: binary from `WENART_LIBREDWG_BIN` (default `/workspace/tools/libredwg/bin`, then `PATH`); `dwg2dxf -y
  --as r2018 -o <out>/converted/<stem>.dxf <in>` (fall back to the default output version when `--as` fails; record
  which); `out_dir` required (never write into the project folder); audit with `ezdxf.recover` (errors → every element
  of the file `unverified` + warning); entity counts of the DXF modelspace by type recorded in `documents[]`; the
  version string from the `VERSION` file. ezdwg is removed from the automatic chain.
- `stages.py`: the converter version is an input of the pipeline fingerprint.
- `intake.py` / `docs/intake.md` / report hint: "DWG is read with LibreDWG 0.14 (beta); if it fails, export DXF". A DWG
  next to a same-stem DXF still loses to the DXF (no double counting).

### 5.2 Generic DXF adapter (`dxf_generic.py`)
- Used when the DXF has none of the synthetic layers (`DUVAR`, `KAPI`, `PENCERE`, `MOBILYA`). Modelspace entities,
  with INSERTs exploded recursively (`virtual_entities`, transformation applied, the block-name chain kept on each
  stroke): LINE, LWPOLYLINE/POLYLINE (bulges → arcs), ARC, CIRCLE, ELLIPSE, SPLINE (flattened ≤ 5 mm), HATCH (boundary
  paths → closed filled strokes; solid or pattern both count as fill), SOLID, TEXT/MTEXT (plain text, `\P` → new run),
  DIMENSION (`DimensionPrim` from the defpoints and the measurement; text override kept), colour from ACI/true colour
  (BYLAYER resolved). Units: `$INSUNITS` (1 in, 2 ft, 4 mm, 5 cm, 6 m); 0 (unitless) → resolved by the generic scale
  rule from dimension entities (measurement vs text) — no rule → `needs_review`.
- Wall hint layers: names matching `WALL|DUVAR|A-WALL|MUR|PARED` (case-insensitive) → `wall_hint_layers`.
- **synthetic-06** (new, `wenart/synthetic`): a 2+1 flat drawn the "real" way — English layer names (`A-WALL` with
  SOLID hatch, `A-DOOR`, `A-GLAZ`, `A-FURN`, `A-ANNO`, `A-DIMS`), inches (`$INSUNITS=1`), blocks with English names
  (`BED-DOUBLE`, `SOFA-3`, `DINING-6`, `WC`, `BASIN`, `CHAIR`), MTEXT labels `LIVING ROOM` + `14'-0" X 12'-0"`,
  feet-inch dimensions, one open kitchen; plus `synthetic-06.dwg` written by LibreDWG `dxf2dwg` (R2000, ANSI_1252, no
  MTEXT rotation) and committed with its sha256; truth `building.json` from the generator. Tests: DXF and DWG runs give
  identical buildings (paths and converter strings aside) and match the truth.

## 6. Area L – look, cameras, library filter, Blender

### 6.1 AgX Punchy
`render.py`: `LOOK = "AgX - Punchy"`, `RENDER_CODE_VERSION = "m7.1"`, `view_transform` and `look` added to
`key_settings`; `window_pull` passes the look explicitly to `save_display`; `stages.ALT_LOOK = "None"` so `look_alt`
pairs are A = Punchy (main), B = None (the M6 default). Tests pinning `"m6.1"`, `look == "None"` and the alt-look
argv are updated (§1.5 lists them). Exposure metering is scene-linear, so EV and white balance do not change.

### 6.2 Views
`camsearch.plan_room`: rooms whose `RoomModel.pieces` (non-decor furniture after layout and decor) is empty get
`EMPTY_ROOM_VIEWS = 1`; such a room with area < `MIN_EMPTY_ROOM_AREA_M2 = 2.5` gets 0 views and the scene manifest
lists it under `rooms_without_view` with the reason. `plan.py` uses the same rule on the pre-layout building (rooms
the layout will not furnish: storage, balcony, prayer, hall without allowed types, `empty_rooms: off`).

### 6.3 Library style filter
- `style/profile.py` writes `family` (from `STYLE_FAMILIES`; `null` when none matched; defaults.yaml profile updated;
  Blender's `BUILTIN_DEFAULTS` mirror updated).
- Catalog entries get `styles` (list of families or `neutral`) and, for beds, `has_mattress`. The 31 Poly Haven
  models are tagged by the implementer from the Poly Haven API tags and thumbnails, with the reason in a new `style_note`
  field; `GothicBed_01`/`GothicCommode_01` → `classic`; `old_bed_frame` → removed (no mattress; `bed_single` becomes
  parametric until O adds one).
- `fit_piece(piece, catalog, style_family=None, …)`: candidates whose `styles` contain the family or `neutral`
  (all candidates when `style_family` is null); none left → parametric with reason `no model for style <family>`.
  `fit` and `refit` get `--style <out>/style.json` (refit is the one that matters: it runs after the final style).
  `catalog.validate` accepts `source ∈ {polyhaven, objaverse}`, `licence ∈ {CC0, CC-BY-4.0}`; a CC-BY entry needs
  `author`, `source_url`, `attribution`.
- Licence gates (`assets/fetch.py`, `assets/models.py`, `blender/furniture.py`): models may be CC0 or CC-BY-4.0 with
  attribution; textures and HDRIs stay CC0; `load_manifest` checks each entry against the rule of its kind (a CC-BY
  model must not break texture fetches). The final report gets an **Attribution** section and
  `results/final/<p>/ATTRIBUTION.md` listing every CC-BY asset used in that project's renders.

### 6.4 New parametric types and geometry
- `stair`: steps from the drawn flights (tread depth from the drawn spacing, riser 0.17 m `assumed`, rising in the
  direction away from the flight end that touches the hall's free side — `assumed` and recorded); a dog-leg gets a
  landing at the turn; the second flight continues to the ceiling; the ceiling over the stair footprint is cut
  (stairwell void, `assumed`); a simple handrail on the free side. Unknown direction → steps rise along +local Y and
  the manifest says so.
- `side_table` (round when the cluster is round: a circle stroke fits ≥ 90 % of its points; else square), `floor_lamp`
  (base, pole, fabric shade; no light source), `plant` (the decor plant model scaled to the footprint).
- Doorless openings: cut through the wall up to 2.10 m (`assumed`), no frame, no leaf. Virtual separators: no
  geometry; floors and ceilings of the two rooms meet at the line (the floor material is continuous when both rooms
  use the same slot). Site elements are not built.
- Rooms of type `dining` use the living slots; `prayer` the living slots, decor off.

### 6.5 Layout and decor
`ALLOWED_TYPES["dining"] = ("table_dining", "chair", "dresser", "bookshelf")`, anchor `table_dining`; `prayer` not
furnishable (it stays empty, 1 or 0 views by §6.2); `side_table`, `floor_lamp`, `plant` are not offered to the layout
(documented pieces only). Decor skips `prayer` rooms.

### 6.6 Interface to O
`catalog.load()` merges `wenart/furniture/catalog_objaverse.json` (O's file; absent → nothing merged) after
`catalog.json`; both pass `validate`. Objaverse entries carry the same frame fields (`front_axis`, `bbox_m`, …) plus
`glb` instead of `gltf`, `sha256_glb`, `author`, `source_url`, `attribution`, `licence`, `styles`, `has_mattress`.

## 7. Area O – Objaverse library (pod)

### 7.1 Survey (`python -m wenart.assets.objaverse survey --out /workspace/assets/objaverse`, CPU on the pod)
1. Download `lvis-annotations.json.gz`, `object-paths.json.gz` and the metadata shards of the candidate uids
   (`HF_HUB` from the pod; never in the session).
2. LVIS categories → types (`objaverse.yaml`; exact category names verified against the downloaded annotation file):
   `bed` → bed_double/bed_single by size, `sofa`, `armchair`, `dining_table`, `coffee_table`, `bookcase` →
   bookshelf, `wardrobe`/`armoire`, `nightstand`, `chest_of_drawers_(furniture)` → dresser, `desk`, `toilet`, `sink` →
   washbasin, `bathtub`, `refrigerator` → fridge, `stove`, `lamp` → floor_lamp (by height), `flowerpot` → plant.
   No category for `tv_unit`, `kitchen_counter`, `wardrobe` built-ins: those stay parametric.
3. Licence from the metadata: keep only CC0 and CC-BY 4.0 (exact metadata strings verified on the pod and written
   to `objaverse.yaml`; NC, ND, SA, "free standard" and unknown are refused).
4. Prefilter: face count 2k–400k, ≤ 40 MB, has textures or vertex colours; rank by `likeCount` then `viewCount`;
   ≤ 30 candidates per type.

### 7.2 Thumbnails and judging (GPU, on the pod)
- Blender (Cycles GPU, 32 samples, 384 px): 4 views (front, 45°, side, top) of each GLB normalised to its bbox; bbox
  in metres after a unit guess (largest side vs the type's size table: × 1, 0.01, 0.0254, 0.001 tried, the one in
  range kept; none → refused).
- Two VLM passes (Qwen, GLM) on a 2 × 2 sheet: `{"is_single_object", "matches_type", "photoreal_quality": 1..5,
  "has_mattress": bool|null, "styles": [family enum ∪ neutral], "front_view": 0..3|null}`.
- Accept: both `is_single_object` and `matches_type`, both quality ≥ 4, beds both `has_mattress`, bbox aspect within
  the type's range; `styles` = intersection of the two answers (empty → `neutral` only if both include it, else
  refused); `front_axis` from the agreed `front_view` (else the type convention, `front_axis_confidence: low`).
- Output: `wenart/furniture/catalog_objaverse.json` (committed from the pod results; ≤ 6 models per type), thumbnails
  `results/library/<type>/<uid>.jpg` (256 px), `results/library/library_report.md` (counts per type, refusals by
  reason, attribution list). Budget ≤ 25 min of pod A.

### 7.3 Use
`models.fetch_model(..., source="objaverse")` downloads the GLB by uid (sha256 checked against the catalog) into
`/workspace/assets/models/objaverse/<uid>.glb`; `blender/furniture.resolve_asset` accepts `.glb`.

### 7.4 If the survey finds too little
Fewer than one accepted model for a (type, family) → the fit uses parametric meshes for it (honest, reported). Nothing
is generated.

## 8. Area V – added-object detection and realism v2

### 8.1 Detector (`wenart/gate/detect.py`, venv-polish)
- OWLv2 `google/owlv2-base-patch16-ensemble` @ `cfd3195ba4ea9592eec887ded089f4c08eff231d` (Apache-2.0), added to
  `gate/models.yaml` (`detect` key; `tests/test_m5_config.py` pin updated) and to `pod_setup_polish.sh part_models`.
- Queries: one per furniture type in plain words ("a bed", "a sofa", …) plus "a door", "a window", "a lamp", "a
  potted plant", "a picture frame", "a rug", "a vase", "a cushion", "a mirror", "a television". Run at 960 px long side
  on the Cycles image and the polished image of a view; boxes with score ≥ `t_det`.
- **Added object** = a polished box (score ≥ `t_det`) with no Cycles box of the same query group at IoU ≥ 0.3 and not
  covered ≥ 50 % by an expected element of a compatible type (`coverage_map`). **Confirmed** when its score ≥
  `t_strong`, or a VLM extra of either pass overlaps it at IoU ≥ 0.3. A confirmed added object rejects the polished
  image (`polish_decision` reason `added_by_polish`); unconfirmed ones are listed (advisory).
- `t_det`, `t_strong` from calibration (`check.yaml detector:` block): positives = the insertion controls (normal
  render as "polished", hidden render as "Cycles"), negatives = accepted polishes of M6 and benign perturbations (JPEG
  q70, noise, blur) of Cycles images. Targets: insertion confirmed ≥ 60 %, false confirmed on negatives ≤ 3 %. If the
  targets are missed, the detector stays advisory and the report says so.
- `combine_extras`: a single-pass VLM extra confirmed by a detector box (IoU ≥ 0.3) counts as confirmed.
- Full runs ask the VLMs about the controls too (`--kinds cycles,polished,controls`), so removal and insertion are
  measured every run; the detector runs in phase 6 next to the gate (stage `detect`).

### 8.2 Realism v2 (`vision_check/realism.py`)
- One call per (pair, aspect, order, model): four short prompts (materials, lighting, furniture, photo), each asking
  only its aspect: "Which of the two images looks more like a real photograph **in its <aspect>**?" with the cues of that
  aspect only; schema `{"winner": enum, "confidence"}`; the enum order and the order in which the question names the
  images alternate with the call parity (`order ab` → "Image 1 … Image 2", enum `[image_1, image_2]`; `ba` → "Image 2 …
  Image 1", enum `[image_2, image_1]`).
- Keys `realism2|<set>:<cam>|<aspect>|<order>`; answers in `ab/answers_realism2_<slug>.json` (M6 answers untouched);
  `input_sha256` hashes the per-call prompt.
- Sets: `ctl_*` (4, 8 views each), `null_identical`, `null_reencode`, `nuisance_ev`, and `look_alt` (Punchy vs None)
  on 32 cameras across the projects of the run (≥ 10 rooms). `m5_vs_m6` is not repeated (needs the M5 renders; M6
  reported its evidence). The null-identical set is asked with `workers 1` (determinism test without batching).
- Signal rule, decision rule, `halo` and position bias unchanged (computed over the per-aspect calls).
- `docs/milestone6.md` §6.1 prompt tests move to this spec's §8.2 code block (below), `tests/test_realism_ab.py` follows.

```text
Look at the two images. Both show the same interior from the same camera.
Question: which image looks more like a real photograph in its {aspect_name}?
Judge only {aspect_name}: {aspect_cues}
Answer with the image whose {aspect_name} is more photographic. There is no tie.
```
(`aspect_name`/`aspect_cues`: materials — "surface texture, reflections, wear, believable material scale"; lighting
— "light falloff, soft shadows, window light, no flat fill"; furniture — "proportions, contact with the floor,
soft goods, believable detail"; photo — "the image as a whole: camera, exposure, colour, absence of render artefacts".)

### 8.3 Interface to R
New CLI steps: `python -m wenart.gate detect <out> --views … --out <out>/detect/` (phase 6, after polish attempts are
known); `python -m wenart.gate detect-calibrate …`; `python -m wenart.vision_check realism2 …` replacing `realism` in
the AB judge phase (old command kept).

## 9. Area R – orchestrator, runner, report

### 9.1 Stages and phases
- New project stages (numbers re-assigned contiguously; `tests/test_run_stages.py` pins the new table):
  `recognize` (after `pipeline`; holder GLM then Qwen; reuse by answer keys), `pipeline_final` (CPU; fingerprinted
  with the answers as inputs; skipped `no questions` when the first pipeline exit was 0), `detect` (holder gate;
  skipped `polish off` / `smoke profile`).
- Phase 2 (GLM) runs when photos **or** recognition questions are pending; phase 3 (Qwen) answers the
  recognition questions first, then runs `pipeline_final` and `fit` again for those projects, then the layout. A project
  whose pipeline exits 4 is `pending` until `pipeline_final`; its final state comes from `pipeline_final` (0 ok, 1
  needs_review). `REVIEW_STAGES` gets `pipeline_final`; `SKIP_REASONS` gets `no questions`.
- Server starts stay ≤ 4 per pod (GLM phase 2, Qwen phase 3, Qwen phase 8, GLM phase 9); `plan.py STARTS` unchanged.
- `--kinds cycles,polished,controls` for the check; the detector step feeds `combine`.
- vLLM tier: `server_seqs(mem) = 8 if mem ≥ 80000 MiB, 4 if ≥ 40000, else 2`; `server_args(8)` = `--max-model-len
  32768 --max-num-seqs 8`. Measured in pod A; if a model fails to start with these flags, the tier falls back to 4.
- `full.sh`: header `--gpu 'RTX PRO 6000' --disk 150`; setup parts add `libredwg`; `RUN_LIBRARY=1` runs the O survey
  (pod A only).
- Copy rules: `debug/*.png` of public projects (≤ 3 MB each), `recognition/answers_*.json`, `recognition/crops/*.png`
  (≤ 200 per project), `detect/*.json`, `results/library/**`.

### 9.2 Time rule
`plan.py`: `GPU_SPEED = {"RTX PRO 4500": 1.0, "RTX 4090": 1.1, "RTX PRO 6000": <measured in pod A>, default 1.0}`
applied to the per-view and per-project minutes (not to downloads or server starts); recognition questions × 2 models
× `EST_VLM_CALL_S / seqs`; window pull + 1 s per view. `project_entry` gives a project that exits 4 its time from the
first pipeline's counts (it no longer gets 0 minutes).

### 9.3 Report
- Units per project (imperial lengths in feet-inches, metres in brackets).
- real01 (and every project with polish on): a **side-by-side sheet** per room, Cycles left, polished right, with the
  gate and check decisions (user decision 4: decide polish again after looking at real01).
- Recognition section: AI-typed pieces with both answers; raster pages with their evidence; site elements; separators.
- Attribution section (CC-BY assets).
- `NEEDS_REVIEW_HINTS`: DWG text updated; raster hints ("no page quadrilateral", "no dimension readable").

### 9.4 Runner
`GPU_PRIORITY` unchanged (RTX PRO 6000 first); `tests/test_full_job.py` header pin follows `full.sh`. Nothing else.

## 10. Pods and budget

Today (3 Oct, UTC) spent $2.66 of $10.00. RTX PRO 6000: $2.09/h live, HIGH stock in EU-RO-1 at 06:40 UTC. A 115-min
pod's worst case is $4.01 (under the $5 action rule, no `--over-5-ok` needed).

| Pod | Content | Max minutes | Worst case |
|---|---|---|---|
| A | setup (libredwg, vllm, polish venv + OWLv2), **recognition** answers for real01, synthetic-02 (scan, photo), synthetic-06, the real01 raster fixtures; Objaverse survey + thumbnails + judging; detector calibration on synthetic-01 controls (rendered in this pod: 8 hides) + M6 accepted polishes on the volume; timings for the GPU speed factor (render 10 views, polish 4 attempts, vLLM 8-seq tier); GPU tests `test_recognition.py`, `test_library.py` | 75 | $2.62 |
| B | full run: **real01**, synthetic-01, synthetic-04, synthetic-02 (raster, now a normal project), synthetic-06 | 115 | $4.01 |
| C | full run: synthetic-03, synthetic-05 + realism v2 A/B (judge phase) | 115 | $4.01 |

Pods run one at a time; pod C is on the next UTC day if A + B leave less than $4.01 today. Before pod A: the CPU
suite green here, `python -m wenart.run plan` for all projects, the smoke e2e. A cut pod resumes with the same
command. Every pod logged in `docs/gpu-log.md`; no pod left running. Ask the user before any action over $5 or any
change to the limits.

## 11. Tests (CPU unless marked)

- G: units (every accepted spelling, round trips, pairs, areas, ambiguity rules); hatch-group detection on synthetic
  combs (spacing, angle, colour); mask decomposition on L/T/+ junctions and real01 (IoU ≥ 0.97); dimension finder
  (arrowheads, ticks, dots, extension lines; real01's two); scale rules (each branch, the corroboration, a rejected
  provisional scale); openings (gap classes, double doors, small gaps merged, continuous-wall doors/windows); plot vs
  building (real01; a plot touching the house is building); separators (end-to-wall, end-to-end, kept/dropped by the
  label rule); label merging and the English vocabulary table (every row); size-label checks; clusters (merge rules,
  details dropped, outline strokes removed); stair and counter rules; front rules; `tests/test_real01.py` acceptance
  (§2.10); synthetic-01…05 buildings unchanged (`test_matches_truth`).
- Y: crop rendering deterministic (sha), prompt/schema strict, two-pass rule table (agree, disagree, size veto,
  not_furniture, room veto), answer store reuse, CLI exit codes with a fake server.
- S: rectification on synthetic photos (corner error ≤ 1 % of the side), deskew, both wall styles, arc fitting, the
  §4.3 targets with saved answers (`tests/fixtures/recognition_answers/` from pod A, fake answers before that), the
  evidence-only rule for secondary raster pages.
- D: dwg.py with a stand-in `dwg2dxf` (args, version file, out dir, audit), with the real binary when present (skip
  otherwise): synthetic-06 DWG = DXF; generic DXF adapter (inserts exploded, block names kept, units 1/2/4/5/6/0,
  hatches, dimensions); synthetic-06 truth.
- L: look constants and render key; empty-room view rule; style family in the profile; style filter in the fit;
  licence gates (CC-BY model ok with attribution, CC-BY texture refused, manifest re-check per kind); stair, side table,
  floor lamp, plant meshes (Blender CPU tests, skip without Blender); doorless opening cut; virtual separator no
  geometry; stairwell void.
- O: survey filters on a canned metadata sample (licences, categories, prefilter, ranking), unit guess, accept rule.
- V: detector decision on canned boxes; calibration maths; combine with single-pass extras; realism v2 keys, prompts
  (verbatim from §8.2), enum order alternation, outcome per aspect, controls; `--kinds` includes controls.
- R: stage table, phases with `pending` projects (exit 4), recognize/pipeline_final ordering, server starts ≤ 4,
  vLLM 8-seq tier, plan golden output including real01, copy rules, report sections (units, side-by-side, attribution),
  full.sh static checks.
- GPU (pods): `test_recognition.py` (answers complete, §4.3 targets, real01 AI typing ≥ 80 % and no wrong verified
  type), `test_library.py` (catalog_objaverse valid, licences, sha256), `test_full_run.py` (real01 `ok`; every
  RUN_TEST project `ok`; synthetic-02 `ok`), `test_render.py` (Punchy in the manifest; empty rooms ≤ 1 view),
  `test_check.py` (insertion measured; detector targets recorded), `test_realism.py` (v2 summary).

## 12. Done criteria

CPU suite, smoke e2e and `wenart.run plan` green here; pods A, B, C exit 0 (resumed pods count); real01 `ok` end to
end with polished/Cycles side-by-side sheets and the reference acceptance met (§2.10); synthetic-01…06 `ok` (02 via
the raster path); the DWG of synthetic-06 equal to its DXF; GPU tests green; detector calibration and realism v2
reported (whatever they say); results committed under `results/`; `docs/plan.md`, `docs/progress.md`,
`docs/gpu-log.md`, `docs/synthetic.md`, `docs/intake.md` updated; no pod running.

## 13. Risks

| Risk | Mitigation |
|---|---|
| Real plans vary (hatch styles, layer-less PDFs, overlapping text) far beyond real01 | the generic core logs every rule that fired; anything not understood is `unverified` or a warning, never guessed; the debug image shows it |
| Separator rule splits or merges open-plan rooms differently from the architect's intent | separators only where two names would share a face; every separator is listed and drawn; size labels cross-check |
| VLMs disagree on most symbols (M2: symbols 0–10 % on full pages) | crops are per piece at a readable scale with an isolated view and a scale bar; disagreement keeps the drawn footprint (unknown + unverified), so geometry is never lost |
| Raster wall detection too noisy on photos | photos are secondary when a scan or vector exists; targets per page; failures → `needs_review` with the reason |
| LibreDWG 0.14 is beta | audit + entity counts; DXF export remains the user's fallback |
| Objaverse quality and licences | strict licence filter (CC0/CC-BY only), two-judge acceptance, thumbnails committed for review, attribution file |
| AgX Punchy breaks the gate validation (more contrast) | every polished project is re-calibrated and validated; a failed validation gives Cycles finals (existing rule) |
| Time on the new GPU unknown | pod A measures the speed factor before the full runs |
| real01 default style (no brief) is not what the user wants | the report says the style is the default; a `projects/real01/brief.yaml` from the user re-runs only style → render → polish → check (fingerprints) |

## 14. Sources (checked 3 Oct 2026)

- LibreDWG tags via `git ls-remote https://github.com/LibreDWG/libredwg.git` (0.13.3, 0.13.4, 0.14 = d9468ae, nightly
  0.14.NNNN); build verified in the session (`cmake`, `ninja`).
- Hugging Face API: `allenai/objaverse` (sha 21e4e142159e2153706c23a3a02e55cec5591cea, ODC-By, per-object licences);
  `google/owlv2-base-patch16-ensemble` (Apache-2.0, cfd3195ba4ea9592eec887ded089f4c08eff231d);
  `IDEA-Research/grounding-dino-base` (Apache-2.0); `microsoft/Florence-2-large` (MIT).
- RunPod `/v2/catalog/gpus` via `scripts/gpu_run.py gpus` (3 Oct 2026 06:40 UTC): RTX PRO 6000 96 GB $2.09/h HIGH.
- real01 measurements: `pdfplumber` 0.11.10 in the session (numbers above).
