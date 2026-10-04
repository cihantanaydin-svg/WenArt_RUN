# Milestone 7 – real projects in: CAD PDFs in feet or metres, DWG, scans and photos; style-true furniture, AgX Punchy, better checks

Goal: the user's first real project (`projects/real01/real01.pdf`, an AutoCAD 2018 PDF of a 30' × 50' Indian house
plot) runs from the project folder to final, checked renders with the same one command as the synthetic projects;
DWG files and scanned or photographed plans stop ending in `needs_review` by default; and the decisions of
3 Oct 2026 (items 3, 5, 6, 7, 8, 9 in `docs/progress.md`) are built. The no-hallucination rules stay as they are:
geometry comes from vector entities (or, for rasters, from deterministic image processing), AI only names what the
geometry already shows (two passes that must agree, checked against size tables), and everything else is
`unverified`, `assumed` or a listed conflict.

Research and prototypes (3 Oct 2026, session scratch, not committed):
- real01 (`pdfplumber` 0.11.10): 1 page, 842 × 595 pt, 163 chars, 27,259 lines, 9,592 curves, 26 tiny rects (the
  keypads of two telephone symbols), no images, no layers, line widths 0.72 and 0. Walls are **21,316 hatch lines at
  135° (comb step 0.127 pt ≈ 3 mm)**, visually solid, bounded by 0°/90° black outline strokes (one 48-vertex outline
  polyline of 94.7 m traces all wall faces and runs across every window and door gap). The two overall dimensions are
  red lines with filled red arrowheads and the texts `50'` (horizontal) and `30'` (upright, in the gap of a vertical
  line): arrow tip to tip 621.72 pt ↔ 50 ft and 373.08 pt ↔ 30 ft, **12.435 pt/ft (0.013 % apart)**. All 8 room-size
  labels are within 0–3.2 % of the measured clear sizes. Wall thicknesses from the outline pairs: **0.150 m (6″) and
  0.229 m (9″)**; the plot wall 0.150 m. Pdfplumber's curve `pts` hold only path vertices: the door arcs (single cubic
  Béziers) must be flattened from `curve['path']`.
- Openings on real01 (vector jambs and Bézier-fitted arcs): 5 doors (sweep 85°, hinge 20–35 mm from a gap end, r/g
  0.94–0.95), but only the entrance door lies between two collinear pieces of one wall run; the bath and store doors
  lie between a free wall end and the face of a perpendicular wall, and the two bedroom doors share one run gap that
  the end of the wall between the bedrooms splits in two. 9 windows (2 parallel lines each in the wall band), 3
  doorless gaps (kitchen–dining 1.60 m, pooja–drawing 1.02 m, lobby–drawing 1.83 m).
- Furniture strokes: once the wall outline strokes are removed segment by segment, proximity clusters give the sofas,
  coffee table, round piece (0.43 m), stair, counter, door leaves, two "bed + 2 nightstands" groups (2.77 m wide) and one
  "table + 6 chairs" group (1.66 × 1.98 m): touching pieces merge at any distance threshold from 2 to 20 mm. A
  polygonize prototype finds the table (0.74 × 1.24 m) and the nightstands as closed contours. The stair is 8
  full-width tread strokes (1.527 m, 0.253 m apart) with duplicated half-width strokes on the left half and a centre
  divider, plus a 0.66 m landing strip. The kitchen counter is 4 separate line objects forming an L at 0.61 m depth.
  The plants in the garden strip are dark-green fills (9 identical clusters).
- The same plan rasterised at 150 dpi and opened with a 5 × 5 kernel gives a wall mask with IoU 0.89 against the
  vector mask. On the synthetic-02 scan (outline walls, continuous through openings) a naive parallel-pair rule reaches
  only IoU 0.25 (dimension chains and furniture sides pair up); with dimension lines removed and seeded growth from the
  outer loop IoU 0.81. Tesseract (psm 11, eng+tur) reads all 6 dimension texts of the synthetic-02 scan when run at 0°
  and 90° (conf ≥ 85) but 0/5 room labels; blanking all its boxes erases 37 % of the wall ink. The synthetic scans carry
  no dpi metadata; the photo's page quad has a mean side ratio 2.7 % off the sheet ratio.
- The current pipeline stops real01 at `needs_review` ("no plan title found"); even with a title it would find no walls
  (line-width buckets), no scale (needs 3 dimensions in metres) and only room type `other`.
- DWG: LibreDWG tag `0.14` (commit d9468ae948b8f07a08efa756c19f8916052358c0, 27 Jun 2026; **no 0.14.1 exists**) builds
  from git with cmake/ninja (static: `-DBUILD_SHARED_LIBS=OFF`, 2 min 41 s on 4 cores, 16 MB binary). `dwg2dxf` without
  `--as` reproduces LibreDWG's AutoCAD reference DXFs (R14–R2018) and gives buildings identical to the DXF runs for DWG
  copies of synthetic-01/04; **with `--as r2018` the modelspace comes out empty (rc 0, audit clean)**. `dxf2dwg` writes
  rotated dimensions without their angle and measurement (ezdxf then measures 0): dimensions must be measured from
  geometry. ezdwg 0.12.12 is unusable as a fallback. ezdxf maps ACI 7 to white.
- Hugging Face API (from the session): `allenai/objaverse` (rev 21e4e142159e2153706c23a3a02e55cec5591cea, ODC-By 1.0,
  per-object licences in 160 metadata shards; LFS downloads are blocked here, so the survey runs on the pod);
  `google/owlv2-base-patch16-ensemble` (Apache-2.0, rev cfd3195ba4ea9592eec887ded089f4c08eff231d);
  `IDEA-Research/grounding-dino-base` (Apache-2.0) and `microsoft/Florence-2-large` (MIT) surveyed, not used.
- Six read-only mappers listed the hook points and pinned tests; five reviewers checked the draft of this spec against
  the code, the rules, real01, synthetic-02/DWG and the orchestrator (73 findings, 11 blockers, all applied here); two
  independent readers plus a reconciler wrote `tests/fixtures/real01_reference.yaml` (§2.10).

Scope (areas, §1.6 owns the files):
1. **G** – generic plan core and the CAD-PDF adapter (real01): units, English vocabulary, hatch/fill/outline walls,
   openings from gaps of three kinds, open-plan rooms, plot and exterior, furniture clusters with composite splitting,
   stairs, kitchen counters (§2).
2. **Y** – AI typing of unnamed furniture clusters and raster room labels: crops, two VLM passes, size table (§3).
3. **S** – raster adapter: scans, phone photos, raster-only PDF pages (§4).
4. **D** – DWG through LibreDWG 0.14 and a generic DXF adapter; synthetic-06 (§5).
5. **L** – AgX Punchy, one view for rooms without furniture, style-filtered library, new parametric types, stairs and
   open-plan geometry in Blender (§6).
6. **O** – a larger CC0 / CC-BY library from Objaverse, surveyed and judged on the pod (§7).
7. **V** – detection of objects the polish adds, insertion measured every run; realism protocol v2 (§8).
8. **R** – orchestrator stages, prep pod job, 96 GB tier, time rule, report, copy rules (§9).
9. Pods: prep (recognition, library, detector calibration, timings), then full runs of real01 and every synthetic
   project with the new look, then the realism A/B (§10).

Out of scope: TRELLIS.2 or any image-to-3D generation (a change of user decision 7, listed for the user's OK: generated
shapes have no documented provenance; parametric meshes are used where the library has no model), angled or curved
walls (warning; `needs_review` only when part of the outer loop), upper floors the documents do not draw (real01 draws a
stair but no first floor, §6.4), exterior and landscape renders (plot wall, parking and garden are recorded in `site`,
not built), paper space and layouts of DWG/DXF files, sections and elevations, IFC/Revit/SketchUp, hand-written notes,
VLM-only scales for rasters (a raster page needs dimension texts that OCR can read, §4.3).

## 0. Decisions (changes to `docs/plan.md` and earlier specs)

| Before | Now | Why |
|---|---|---|
| Plan pages need a Turkish title (`KAT PLANI`, …), else class `other` (skipped) | a vector page (PDF or DXF/DWG) with no title but with ≥ 2 **room-name labels** (English or Turkish) and a wall structure is a `floor_plan` (confidence 0.6, classifier `generic_labels`); a project with exactly one plan page and no level title gets level `L0` "Ground floor" as an **assumed** value (`levels[].label_source: "assumed"`, warning, report) | real01 has no title; a level title is not geometry. Missing scale or an open outline still stop the project |
| Lengths are metres, areas m² | one parser for m, cm, mm, feet and inches, size pairs and areas in both systems; reports show imperial projects in feet-inches with metres | real01 is imperial |
| Scale: a scale note, or ≥ 3 dimension texts within 1 % | + **2 dimensions within 0.5 %** corroborated by ≥ 2 room-size labels within 5 % (confidence 0.85); 1 dimension + ≥ 3 size labels (0.7, warning). Size labels alone never give a scale. On raster pages a scale note counts only with a verified pixel size (raster-PDF render dpi, PNG pHYs, TIFF resolution) and never against the dimensions | real01 has two dimensions; scans carry no dpi |
| Walls = 0.5 pt rectangles (PDF) or layer `DUVAR` (DXF) | walls from a **wall mask** (hatch groups, dark grey fills, closed thin outlines, wall-layer hatches, raster masks), decomposed into rectangles whose faces snap to outline strokes; the old paths stay for the synthetic conventions | real plans hatch or fill walls |
| Openings: door blocks / arcs and window rectangles on continuous walls | gaps of three kinds (between run pieces, **from a free end to a wall face**, **run gaps split by a perpendicular wall end**), classified by their content (arc + leaf → door, band lines → window, empty → doorless `opening`); the wall is extended to host a drawn door; continuous-wall symbols keep working | 4 of real01's 5 doors are not between two pieces of one run |
| One label per wall-bounded face | doorless gaps are openings; **virtual separators** (end-to-wall, end-to-end, ≤ 2.4 m, only from free ends whose gap is empty) are kept only when two room names would share a face or a stair would share a labelled face; label lines are merged (`Bath+` / `Toilet`) and the size line attached | real01 is open plan (drawing + dining share one face) |
| Everything inside the outer loop is the building | wall components without indoor labels whose convex hull contains the building are the **plot** (`site.boundary_walls`); exterior labels (Parking, Garden, …) become `site.areas`; site decor is recorded; nothing of it is built | real01's compound wall is a C shape around the house |
| Furniture types from block names (DXF) or `unknown` (PDF) | **clusters** of non-wall strokes (composite groups split into closed-shape seeds) give footprints from the geometry; stairs and kitchen counters by deterministic rules; other types from **two VLM passes (Qwen3-VL-8B, GLM-4.6V-Flash) that must agree** and fit the size table; otherwise `unknown` + `unverified` with both candidates. Clusters both passes call `not_furniture` stay in the building (`build: false`), so the room keeps `has_documented_furniture` | CLAUDE.md furniture and no-hallucination rules |
| Evidence methods `vector`, `ocr`, `ai`, `derived` | + `raster` (deterministic image processing) | trust order vector > raster/ocr > ai |
| Room types | + `dining`, `prayer` (pooja; never furnished by AI, no decor) | real01 |
| Furniture types (24) | + `stair` (fixed equipment, built like walls), `side_table`, `floor_lamp`, `potted_plant` (`plant` stays the decor class of the vision check) | real01's stair and round piece |
| Raster pages: class `other`, skipped | scans, phone photos and raster-only PDF pages go through the raster adapter; dimension texts from Tesseract (0° and 90°) give the scale; room labels from two VLM passes or one pass equal to Tesseract; a raster page of a level that also has a vector/DXF page is **evidence only** (Tesseract and geometry, no AI requests; door/window/labelled-room counts compared ± 1) | user decision 9; DWG > vector PDF > scan > photo |
| DWG: LibreDWG 0.14.1 (does not exist), then ezdwg | LibreDWG **0.14** (pinned d9468ae, static build, `dwg2dxf` without `--as`), empty modelspace → `needs_review`; converter version in the pipeline fingerprint; same-stem DXF wins in every project; no ezdwg | measured above |
| DXF: synthetic layer and block names only | a **generic DXF adapter** (any layers; HATCH even-odd, INSERT names and ATTRIBs, dimensions measured from geometry, ACI 7 = black, `$INSUNITS` incl. inches/feet) feeds the generic core when the synthetic layers are absent | real DWGs |
| Default look AgX, look `None` | **`AgX - Punchy`** (`RENDER_CODE_VERSION = "m7.1"`, look and view transform in the render key); `look_alt` A/B = Punchy (A) vs None (B) | user decision 6 |
| Rooms get 1–3 views by area | rooms with **no furniture after layout and decor get 1 view**; such rooms < 2.5 m² get **none** (listed) | user decision 8 |
| Any library model whose box fits | library models carry `styles` and beds `has_mattress`; **refit** takes a library model only when its styles contain the project's style family or `neutral`; beds without a mattress dropped | user decision 7 |
| Poly Haven CC0 only | + Objaverse objects with licence **CC0 or CC-BY 4.0** (no NC/ND/SA), judged by two VLMs on thumbnails, fronts agreed; full CC-BY credits and the ODC-By notice in every results folder that shows them | user decision 7 |
| TRELLIS.2 planned as a fallback | **not built in M7** (needs the user's OK) | provenance; see out of scope |
| Insertion practically never confirmed | **OWLv2** boxes on Cycles vs polished images; a box confirmed by its strong score or by either VLM's extra rejects the polished image (decided in `combine`); thresholds calibrated on the 29 M6 hide/normal pairs; controls asked in every full run | user decision 3 (absolute flags stay advisory) |
| Realism: 4 aspects in one call | **one aspect per call**, both orders, image order also alternated inside the question and the answer enum; new files `realism2*`; M6 answers kept | user decision 5 |
| vLLM ≥ 40 GB: 16k context, 4 seqs | + ≥ 80 GB tier: 32k context, 8 seqs, probed per model in the prep pod and committed (`check.yaml models.<k>.max_seqs`) | RTX PRO 6000 (96 GB) |
| Time rule measured on the PRO 4500 | + `GPU_SPEED` per GPU (measured in the prep pod), recognition calls, server starts with recognition | new default GPU |
| real01 has no brief | the defaults apply (Scandinavian, …), listed as assumed; a `projects/real01/brief.yaml` from the user re-runs style, refit, build, render, polish, check | the user can give the style later |

## 1. Shared contracts (read before any area)

### 1.1 Units (`wenart/units.py`, new, stdlib only; owner G1)

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
def format_length(metres, system) -> str      # imperial: 11' 3" (nearest inch); metric: 3,40 m
def format_area(m2, system) -> str            # imperial: 110 sq ft; metric: 24,50 m²
FT = 0.3048; INCH = 0.0254; SQFT = 0.09290304
```
- Marks: `'` `’` `′` feet; `"` `”` `″` `''` inches; `ft`, `feet`, `in`, `inch`; `-` or space between feet and inches; `x`,
  `X`, `×`, `*` between pair members. Bare numbers: comma decimal → metres (existing rule); a bare integer is feet only
  with `default_system="imperial"`. `mm`/`cm`/`m` as today. `model.parse_number` and `building._AREA_RE` call this
  module; their existing metric behaviour and tests stay.
- A page's `unit_system` = majority of its parsed lengths (dimensions first, then size labels), ties → metric; stored in
  `LevelExtraction.units_system`, `documents[].unit_system`, `project.unit_system` (the master pages' system).

### 1.2 Generic page model (`wenart/ingest/generic/model.py`, committed foundation)

`Stroke`, `TextRun`, `DimensionPrim`, `MaskLayer`, `GenericPage` as committed (d81b6b4): page units with **y up**,
`Stroke.pts` flattened, `arc` set when a circle fits within 1 % of the radius, `colour`/`fill` RGB 0..1 (DXF ACI 7 and
true-colour white → black), `layer`/`block` for DXF, `to_original` (3 × 3, page units → original image pixels) set for
**every** raster page (deskew rotation for scans, render dpi for raster-PDF pages, homography for photos).
`LevelExtraction` got optional fields (`source_kind`, `units_system`, `level_assumed`, `site`, `separators`,
`candidates`, `wall_mask_png`, `notes`); `OpeningItem` (`virtual`, `line`, `height`, `sill`, `assumed`, `type_raw`);
`FurnitureItem` (`type_method`, `type_candidates`, `extra_evidence`, `details`). Defaults keep every old extractor
unchanged.

`core.extract(page, level_id, file_rel, answers=None, no_ai=False) -> LevelExtraction` runs in this order:
texts → unit system → dimensions (§2.3) → provisional scale → wall primitives and mask → wall rectangles (§2.4) →
gaps and openings on all walls (§2.6) → label blocks (§2.7.2) → plot and building (§2.5) → faces and separators
(§2.7.1) → furniture clusters, rules and candidates (§2.8) → confirm scale with the size labels (§2.3) → apply AI
answers (§3) → shift to the building frame. Without a provisional scale it returns early (scale `None`); the pipeline
stops with `needs_review` as today.

### 1.3 Building JSON additions (`wenart/schema/building.schema.json`, `wenart/building.py`)

Committed foundation (d81b6b4 + this spec): evidence method `raster`; scale method `room_size_label` (corroboration
only); room types `dining`, `prayer`; furniture types `stair`, `side_table`, `floor_lamp`, `potted_plant`; conflict
kinds `label_size_mismatch`, `symbol_type_disagreement`, `raster_count_mismatch`; `openings[].wall_id` may be `null`
**only** with `virtual: true` and `line`; top-level `site`. Added by G (optional fields, no enum change):
- openings keep the names `type` and `sill_height`; new `assumed: ["height", "sill_height"]` lists defaulted values
  (door and doorless height 2.10 m, window sill 0.90 m and height 1.20 m); `type_raw` for unclassified gap content.
- rooms: unlabelled faces keep a non-null placeholder `label` (`UNLABELLED_LABEL` "Oda" on Turkish pages, "Room" on
  English pages) with `label_raw: null` (report prints "—"); new `label_size` `{"text", "width_m", "length_m",
  "measured": [w, l], "status": "ok|conflict|unchecked"}`.
- levels: `label_source: "title" | "assumed"` (+ evidence = the room labels when assumed).
- furniture: `type_candidates`, `type_method` (`block_name` | `rule` | `ai_two_pass` | `none`), `build` (default
  true; false for clusters both passes call `not_furniture`), `stair` (`{"flights": [{"start", "end", "width",
  "lines"}], "landing", "direction", "direction_assumed", "turn_assumed", "void_assumed", "riser_m",
  "riser_source"}`), `counter_run` (`{"wall_id", "strokes"}`).
- `site`: `{"boundary_walls": [{"id": "sw_L0_001", "start", "end", "thickness", "evidence", "kind": "plot|other"}],
  "areas": [{"id": "sa_L0_parking", "label", "label_raw", "label_size", "polygon": null|[...], "evidence"}],
  "decor": [{"id": "sd_L0_001", "kind": "plant|tree|car|other", "center", "size", "evidence"}], "openings": [...]}`.
- `project.unit_system`, `documents[].unit_system`, `documents[].source_kind`, `documents[].pages[].rectified_image`
  and `to_original` (raster pages, §4.1).
- Room-type rules (`building.py`): English keywords (§2.7.2) join `_ROOM_TYPE_KEYWORDS`; an English label with a bath
  or shower word **and** toilet/wc is a bathroom (applied before the priority list; Turkish labels keep wc first, e.g.
  `Banyo/WC` → wc); priority `("wc", "bathroom", "storage", "balcony", "bedroom", "living", "kitchen", "dining",
  "prayer", "hall", "other")`, so `Kitchen & Dining` is a kitchen and `Living / Dining` a living room.
  `normalise_room_label` uses Turkish casing only when the label matched a Turkish keyword or contains Turkish letters,
  plain title case otherwise (keeping `WC`).

### 1.4 Recognition requests and answers (`wenart/recognition/answers.py`, new; owner Y)

The pipeline is CPU-only and runs before any VLM server. It writes questions in **one round**; a GPU stage answers
them; the pipeline re-runs with the answers. Raster scales never wait for AI (§4.3), so every question (symbol types,
room labels) can be asked in the first run.

- `<out>/recognition/requests.json`: `{"schema_version": "0.1", "kind": "recognition_requests", "project", "items":
  [{"key", "task": "symbol_type|room_label", "page", "images": ["crops/<key>_ctx.png", "crops/<key>_iso.png"],
  "context": {...}, "input_sha256"}]}` (paths relative to `<out>/recognition/`).
- `input_sha256` hashes a **canonical description**, not PNG bytes: the candidate's strokes in page metres rounded to
  1 mm (or, for raster crops, the sha256 of the decoded grey pixel array and its shape), the crop box, `CROP_VERSION`,
  the prompt, the schema and the allowed type list. Crops are drawn with `cv2` (LINE_8, no anti-aliasing, fixed sizes, no
  text: the scale bar is a bar) and saved with PIL without metadata, so the same crop has the same hash in the session
  and on any pod.
- `<out>/recognition/answers_<slug>.json` (`slug` from `check.yaml models.<key>.slug`): the M5 `AnswerStore` pattern; an
  answer is reused when key and `input_sha256` match; temperature 0, seed 0, structured outputs, jsonschema-validated.
  Empty, `null` or `""` answers never count as agreement.
- CLI: `python -m wenart.recognition.answers ask <out>/recognition --model-key qwen|glm --server URL --workers N
  [--deadline T] [--seed-answers DIR]` (exit 0 all answered, 3 deadline, 2 server error; `--seed-answers` copies stored
  answers from a results folder whose key and hash match before asking) and `... status <out>/recognition`.
- Pipeline: `python -m wenart.ingest.pipeline <proj> --out <out> [--answers <out>/recognition] [--no-ai]`. Exit codes:
  0 ok, 1 needs_review, **4 = questions written, answers missing** (the building is written in its pre-answer state:
  furniture `unknown`/`unverified`, raster labels from Tesseract only). With `--answers` and complete answer files, or
  with `--no-ai` (unanswered items stay `unverified`), it never exits 4. Evidence-only raster pages never write
  questions.

### 1.5 Internal interfaces of the generic core (G1 text, G2 geometry, G3 integration)

All core functions work in **page metres**: page units × `units_to_m`, y up, no offset. `core.extract` shifts to the
building frame at the end (`transform_to_building = [s, 0, -ox, 0, s, -oy]`, `(ox, oy)` = min corner of the building
walls; raster pages: composed with the page frame of §4.1).

```python
# generic/labels.py (G1)
def room_name_runs(texts: list[TextRun]) -> list[TextRun]
def merge_label_blocks(texts_m: list[TextRun]) -> list["LabelBlock"]                      # §2.7.2
@dataclass class LabelBlock: name: str; name_runs: list[TextRun]; size_text: Optional[str]; area_text: Optional[str]
                             anchor: tuple[float, float]; room_type: str; exterior: bool; evidence: list[dict]
# generic/scale.py (G1)
def find_dimensions(page: GenericPage) -> list["DimCandidate"]                            # §2.3, page units
def provisional_scale(page, dims) -> tuple[Optional[dict], list[str]]                     # scale dict (schema page.scale) + reasons
def confirm_scale(scale, dims, label_blocks, faces_m) -> tuple[Optional[dict], list[dict], list[str]]   # scale, conflicts, warnings
# generic/walls.py (G2)
def wall_primitives(page: GenericPage, units_to_m: float) -> list["WallPrim"]
def wall_mask(page, prims, units_to_m, px_m=0.01) -> MaskLayer                           # page metres
def walls_from_mask(mask, outline_strokes_m, file_rel, page_no) -> tuple[list[WallItem], dict]
# generic/openings.py (G2)
def gaps_and_openings(walls, strokes_m, file_rel, page_no) -> tuple[list[WallItem], list[OpeningItem], list[dict], set[str]]
                                       # merged/extended walls, openings, gap log, ids of strokes the openings own
# generic/topology.py (G2)
def split_plot(walls, openings, label_blocks) -> tuple[list[WallItem], dict, list[str]]   # building walls, site, warnings
def separators(walls, openings, gap_log, label_blocks, stairs) -> tuple[list[OpeningItem], list[dict]]
# generic/symbols.py (G2)
def furniture(strokes_m, owned, walls, openings, texts_m, dims, outline, faces) -> tuple[list[FurnitureItem], list[dict], list[dict]]
                                       # typed pieces (rules, block names), AI candidates, site decor
# generic/core.py (G3)
def to_metres(page, units_to_m) -> tuple[list[Stroke], list[TextRun]]
def extract(page, level_id, file_rel, answers=None, no_ai=False) -> LevelExtraction
```
G1 and G2 unit-test against hand-made `GenericPage`s; G3 wires them, owns the CAD-PDF adapter and the real01 acceptance.

### 1.6 Ownership (parallel implementation, wave 1 then wave 2)

| Area | Wave | Owns |
|---|---|---|
| G1 text | 1 | `wenart/units.py`, `wenart/ingest/generic/{labels,scale}.py`, `wenart/building.py` (vocabulary, priority, casing), `tests/test_units.py`, `tests/test_generic_labels.py`, `tests/test_generic_scale.py`, `tests/test_building.py` |
| G2 geometry | 1 | `wenart/ingest/generic/{walls,openings,topology,symbols}.py`, `tests/test_generic_walls.py`, `tests/test_generic_openings.py`, `tests/test_generic_topology.py`, `tests/test_generic_symbols.py` |
| G3 integration (after G1, G2) | 1 | `wenart/ingest/generic/core.py`, `wenart/ingest/cad_pdf.py`, `wenart/ingest/{classify,pdf_extract,model,rooms,pipeline,debug_image}.py` (vector and DXF-generic branches; the DWG same-stem rule; `_classify_dxf` generic rule calling D's `dxf_generic.collect_texts`), `wenart/schema/building.schema.json`, `docs/examples/building.example.json`, `wenart/report/ingest` parts of `pipeline.write_report`, `tests/test_cad_pdf.py`, `tests/test_real01.py`, `tests/test_{classify,pdf_extract,rooms,pipeline}.py` (except the DWG tests, D) |
| Y AI typing | 1 | `wenart/recognition/{answers,symbols,crops,room_labels,prompts,schemas,vlm_client}.py`, `wenart/recognition/size_table.yaml`, `tests/fixtures/recognition_answers/` (fake answers now, pod answers later), `tests/test_recognition_answers.py`, `tests/test_symbols.py`, the schema/hint tests in `tests/test_recognition_cpu.py`, `tests/gpu/test_recognition.py` |
| D DWG + DXF | 1 | `wenart/ingest/dwg.py`, `wenart/ingest/dxf_generic.py` (incl. `collect_texts(doc)`), `wenart/ingest/dxf_extract.py` (dispatch only), `wenart/synthetic/{blocks,dxf_writer,projects,generate}.py` for synthetic-06 only (not raster code), `projects/synthetic-06/` (generated), `docs/synthetic.md`, `scripts/pod_setup_recognition.sh` (libredwg part), `scripts/cloud-setup.sh`, `wenart/intake.py` (DWG texts), `docs/intake.md`, `tests/test_dwg.py`, `tests/test_dxf_generic.py`, the DWG tests in `tests/test_classify.py` (93–130), the libredwg pins in `tests/test_recognition_cpu.py`, `tests/test_synthetic.py`, `tests/test_intake.py` |
| L look/cameras/library/Blender | 1 | `wenart/blender/*`, `wenart/style/{vocabulary,profile}.py`, `wenart/defaults.yaml` (style block), `wenart/furniture/*` (incl. `prompts.py`, not `catalog_objaverse.json`), `wenart/polish/prompt.py`, `wenart/assets/{fetch,models}.py`, `tests/test_blender_*.py`, `tests/test_camsearch.py`, `tests/test_look_m6.py`, `tests/test_furniture_fit.py`, `tests/test_style.py`, `tests/test_layout.py`, `tests/test_placer.py`, `tests/test_decor.py`, `tests/test_assets.py`, `tests/test_models_assets.py`, `tests/test_polish_parts.py`, `tests/gpu/test_render.py`, `tests/gpu/test_look_m6.py`, `tests/gpu/test_furnish.py` |
| O Objaverse | 1 | `wenart/assets/objaverse.py`, `wenart/assets/objaverse.yaml`, `wenart/furniture/catalog_objaverse.json` (written from the prep pod results), `tests/test_objaverse.py`, `tests/gpu/test_library.py` |
| V check + realism | 1 | `wenart/vision_check/*`, `wenart/gate/{detect.py,models.yaml,models.py,__main__.py}`, `tests/test_vision_check_*.py`, `tests/test_realism_ab.py`, `tests/test_detect.py`, `tests/test_m5_config.py` (pins that change), `tests/gpu/test_check.py`, `tests/gpu/test_realism.py`, `tests/gpu/test_detect.py` |
| S raster | 2 | `wenart/ingest/raster.py`, `wenart/ingest/rectify.py`, the raster branches of `classify.py` and `pipeline.py` (dispatch, `SOURCE_RANK` by kind, evidence-only merge), `wenart/synthetic/raster.py`, the raster evidence of `wenart/synthetic/generate.py` and the regenerated truth of `projects/synthetic-0{1,2}/truth/`, `tests/fixtures/real01_raster/`, `tests/test_raster.py`, `tests/test_rectify.py`, the raster pins in `tests/test_{classify,pipeline,synthetic}.py` |
| R run | 2 | `wenart/run/*` (incl. `stages.ALT_LOOK`, fingerprints, plan rules), `scripts/jobs/{full,prep}.sh`, `scripts/gpu_run.py`, `scripts/pod_entry.sh`, `scripts/pod_setup_polish.sh` (parts), `scripts/pod_requirements.txt` (pins), `wenart/report/*`, `tests/test_run_*.py`, `tests/test_full_job.py`, `tests/test_report.py`, `tests/test_gpu_run.py`, `tests/test_polish_job.py`, `tests/fakes/*`, `tests/fixtures/projects/review-01/`, `tests/gpu/test_full_run.py` |

Tests that fail on the committed foundation (new enums) and who fixes them: L — `test_blender_furniture.py::test_parametric_types_cover_the_schema_and_the_spec_table`, `test_furniture_fit.py::test_catalog_covers_every_schema_type`, `test_layout.py::test_default_sizes_are_the_drawing_block_sizes`, `test_polish_parts.py::test_word_tables_cover_every_vocabulary_slug_room_and_furniture_type`; Y — `test_recognition_cpu.py::test_prompt_matches_schema[symbols]`; V — `test_vision_check_combine.py` (3) and `test_vision_check_prompts.py` (3). Wave 2 starts when wave 1 is integrated and the suite is green. Files outside the table: integrator only (`docs/*`, `CLAUDE.md`, `pyproject.toml`).

## 2. Area G – generic plan core and the CAD PDF adapter

### 2.1 Page classification (`classify.py`, G3)

- Title rule first (unchanged). No title, vector page: `labels.room_name_runs(texts)` gives ≥ 2 runs **and** a cheap wall
  test passes → `floor_plan`, confidence 0.6, `classifier: "generic_labels"`, evidence = the runs. Cheap wall test in
  page units (no scale yet): ≥ 200 strokes of one colour within ± 1° whose median perpendicular step ≤ 0.5 % of the
  page's short side and whose length ≤ 5 % of it (a hatch), or dark grey fills (§2.4), or ≥ 4 closed thin polygons, or
  (DXF) a HATCH/SOLID or closed polyline on a wall-hint layer. Applies to `_classify_pdf` and `_classify_dxf` /
  `_classify_dwg` (texts from `dxf_generic.collect_texts`, which includes block texts and INSERT ATTRIBs).
  `classify_texts([room label])` keeps returning `other` (`tests/test_classify.py:91`).
- Level: title rule; else exactly one plan page without a level title in the project → `L0` "Ground floor",
  `label_source "assumed"`, warning "level title missing: assumed L0 Ground floor". Several untitled plan pages →
  `needs_review` ("cannot order untitled plan pages").
- English level titles: `GROUND FLOOR`, `FIRST FLOOR`, `SECOND FLOOR`, `BASEMENT`, `<n>(st|nd|rd|th) FLOOR`, class words
  `FLOOR PLAN`, `FURNITURE (LAYOUT) PLAN` (case-insensitive).
- DWG with a same-stem DXF (any project, not only intake): the DWG is recorded with `skip_reason "DXF of the same name
  is used"` and is not a review reason.
- PDF pages: paths + chars → vector; paths, no chars, no large image → vector page with texts from Tesseract on a 200
  dpi render (0° and 90°, method `ocr`; text-glyph strokes inside accepted text boxes are not furniture) — the AutoCAD
  SHX-text case (S implements the OCR part in wave 2; until then such pages are `needs_review` "text drawn as
  geometry"); no paths + an image ≥ 50 % of the page → raster (S).

### 2.2 CAD PDF adapter (`wenart/ingest/cad_pdf.py`, G3)

`cad_pdf.read_page(path, page, file_rel) -> GenericPage` with pdfplumber: lines, curves and rects become `Stroke`s with
`colour = stroking_color`, `fill = non_stroking_color if fill`, `width = linewidth` (gray, RGB and CMYK forms
normalised), coordinates converted once from pdfplumber's y-down `top` space to y-up. **Curves are flattened from
`curve['path']`** (ops `m`, `l`, `c`, `h`; ≤ 0.25 pt chord error; `h` or a repeated first point = closed), never from
`curve['pts']`; a flattened curve that fits a circle within 1 % of its radius gets `arc`. Texts: `merge_chars` runs with
box, height and rotation. Zero-length strokes (dots) are kept. `pipeline.py` dispatches pages with `classifier ==
"generic_labels"` (or titled pages without 0.5 pt wall rectangles) to `core.extract`; the synthetic PDFs keep
`extract_pdf_page`.

### 2.3 Dimensions and scale (`generic/scale.py`, G1)

- **Dimension candidates**: a text run that parses as one length (§1.1) and a straight dimension stroke: (a) two
  collinear strokes whose gap midpoint lies inside the text box (within 0.5 × text height of their axis) → the text
  belongs to that line **whatever its rotation** (real01's upright `30'`); or (b) a stroke parallel to the baseline
  within 2.5 × text height. The line's ends need end marks: filled triangles (tip = end), short 30–60° strokes (ticks,
  centre = end), dots, or perpendicular extension lines. Measured = distance between the two ends. DXF
  `DimensionPrim`s come measured from geometry (§5.2).
- `ratio_i = printed_m / measured_units`. Rules, first that holds wins: a scale note (vector pages; raster pages only
  with a verified pixel size, §0) → `pdf_scale_text`; ≥ 3 ratios within 1 % and the majority → `dimension_text` 0.9;
  exactly 2 within 0.5 % → **provisional** `dimension_text`, confirmed at 0.85 when ≥ 2 room-size labels (§2.7.3) agree
  within 5 %; 1 dimension → provisional, confirmed at 0.7 with ≥ 3 size labels within 5 % (warning "scale from one
  dimension, corroborated by N room sizes"). A provisional scale that is not confirmed → `needs_review` ("scale not
  corroborated: …" with the candidates). Every dimension off the chosen ratio by > 1 % → `scale_disagreement`
  conflict.
- real01: `50'` ↔ 621.72 pt, `30'` ↔ 373.08 pt; ratio 0.024511 m/pt; confirmed by 8 size labels (0.0–3.2 %).

### 2.4 Walls (`generic/walls.py`, G2)

1. **Wall primitives** (confidence): *hatch groups* — ≥ 20 straight strokes of one colour and direction (± 1°), length
   ≤ 0.8 m, whose perpendicular offsets form a regular comb (median step ≤ 25 mm) → `vector` 0.95, entity
   `hatch:<group>`; *dark fills* — filled closed strokes with luminance ≤ 0.35 **and chroma (max − min RGB) ≤ 0.10**
   → 0.9 (real01's dark-green plants and red arrowheads are excluded); *outline walls* — closed stroked polygons of 4–12
   vertices, minimum width 0.05–0.60 m, length ≥ 0.4 m, containing no stroke of another cluster → 0.8; DXF hatches/solids
   on wall-hint layers → 0.95; raster: the given mask → `raster` 0.85.
2. Rasterise into a mask at **10 mm/px** (polygons filled even-odd; hatch lines drawn 1 px wide, then a 3 × 3 closing
   and a 1 px erosion). Drop components < 0.02 m² and components none of whose decomposed rectangles has length ≥ 3 ×
   its thickness, unless they touch a kept wall.
3. **Decompose** into rectangles in the dominant orientation pair: maximal strips with constant cross-section (± 1 px);
   at T and L junctions the through-wall keeps the junction, the other wall ends at its face. The union must reproduce
   the mask with IoU ≥ 0.97 (else warning with the missed area).
4. **Snap faces**: each rectangle face moves to a parallel outline stroke segment lying within 20 mm of it along ≥ 50 %
   of the face; thickness = distance between the snapped faces, rounded to 5 mm. Without outline strokes the eroded
   mask decides.
5. Thickness classes (clusters within 15 mm) are reported; real01: 0.150 and 0.230 m (± 5 mm). Non-axis walls (> 3°):
   warning `angled wall not modelled`; `needs_review` only when needed to close the outer loop.

### 2.5 Plot and building (`generic/topology.py`, G2)

- Wall components after the openings of §2.6 are bridged (a door, window or doorless gap joins its two sides). The
  **building** = the components whose faces hold ≥ 1 indoor room-name label block.
- A component **encloses** the building when the building outline lies inside the component's convex hull (a C-shaped
  plot wall open on the gate side counts). Such a component without indoor labels → **plot**: walls to
  `site.boundary_walls` (`kind "plot"`); the exterior label blocks outside the building outline and inside that hull →
  `site.areas` (polygon `null` unless a closed face exists; real01's Parking: label 15'3" × 11'3", measured 15'0" ×
  11'3" between the house wall and the plot-wall line — reported, not a conflict because the area is not closed).
  Every other component without indoor labels → `site.boundary_walls` with `kind "other"` and a warning; never in
  `walls`, never dropped silently. Strokes and clusters outside the building outline → `site.decor` (plants: green
  fills or radial clusters → `plant`; else `other`).
- A face whose only labels are exterior keywords is not a room: it goes to `site.areas` with its polygon. If such a face
  lies inside the outer loop, the outer loop is recomputed from the indoor faces; if that does not close →
  `needs_review` ("exterior area inside the building outline").
- The **outer loop** = the exterior boundary of the building walls with openings bridged; it must close
  (`needs_review` otherwise). Exterior walls = walls touching it. The building-frame origin is the min corner of the
  building walls. A room-name label outside both building and plot → warning + report (not `needs_review`).

### 2.6 Openings (`generic/openings.py`, G2)

- **Runs**: rectangles on one axis line (centre-line offset ≤ 20 mm, thickness ± 30 mm).
  Odd mask pieces (P7, real01 photo), each logged as a page note and in the wall's evidence note:
  - *fused strip*: a door leaf filled into the wall mask along a wall face makes a stretch thicker on one face, so it
    leaves its run and the run sees a false gap. It joins the run (run faces kept, the strip is not wall) when it lies
    between two run pieces, one face is flush (≤ 20 mm), the other is out by ≤ 60 mm (+ 1.5 px on rasters), and a
    door swing explains it (arc of 60–100°, hinged within 0.08 m of the piece, swinging on the strip's side; the
    strip runs from within 0.10 m of the hinge for 0.85–1.05 r + 0.10 m).
  - *end cap*: a piece shorter than its own thickness touching (on one side only) the end of a longer wall of
    another cross-section, ≤ 60 mm (+ 1.5 px) outside its band, on a line with no other wall pieces than such caps
    (a door frame or nub, not a short junction piece of a wall run) is no wall end: no gap is cast
    from or to it, and it keeps no end from being free; the opening runs from wall end to wall end.
- **Gaps** (all three kinds go through the same classifier):
  - (a) *run gap* between consecutive pieces of a run;
  - (b) *end gap*: from a free wall end (no wall within 50 mm of its end face) along its axis to the first wall face hit
    within 3.0 m;
  - (c) a run gap that contains the end face of a perpendicular wall inside the run band is **split** at that wall into
    two gaps (real01's two bedroom doors).
  Gap ends are piece ends or perpendicular wall faces. Width g < 0.25 m → closed (warning); 0.25 ≤ g ≤ 3.0 m →
  classified; > 3.0 m → open (topology decides).
- **Classifier** (strokes within the gap rectangle grown by 0.35 m on both faces; that zone is for classification only):
  - *door*: an arc whose centre (the hinge) lies within 0.08 m of a gap end **or inside the wall band at the gap end**
    (synthetic convention: hinge on the centre line), radius g ± 12 %, sweep 60–100°; or two arcs hinged at both ends,
    radius g/2 ± 12 % (double door). **Leaf** = strokes forming a shape ≤ 60 mm wide, starting within 0.10 m of the
    hinge, length 0.85–1.05 × r, along the arc's start or end radius (optional). Swing side = the face the arc is on.
    Confidence 0.95 with a leaf, 0.85 without.
  - *window*: ≥ 2 straight strokes parallel to the wall axis inside the wall band (faces ± 20 mm) spanning ≥ 80 % of g;
    `sill_height` 0.90 and `height` 1.20 `assumed`. Confidence 0.9.
  - *doorless*: nothing in the band and no arc → `type "opening"`, `height` 2.10 `assumed`, confidence 0.8. **In an
    exterior wall** an empty gap is `status unverified` ("possible undrawn door or window"), listed.
  - anything else → `type "opening"`, `unverified`, `type_raw "unclassified gap content"`, strokes listed.
- A run gap closes inside its run (the run becomes **one** `WallItem`, thickness = length-weighted median, the gap an
  `OpeningItem` on it). An end gap holding a door or window **extends** the free-end wall to the hit face (evidence:
  the piece + the arc/leaf ids, method `derived`, note "extended to host the drawn door"); it is never a separator. An
  empty end gap is a separator candidate (§2.7.1).
- An opening **owns** its arc, leaf, hinge pin, the band lines it used and the jamb/frame strokes entirely within the
  gap ± 0.10 m; §2.8 excludes exactly the owned strokes.
- Continuous-wall symbols (synthetic convention, raster double-line walls): an arc + leaf hinged inside a wall band or
  within 0.08 m of a face (`pdf_extract._door_from_arc` end-point rule), radius 0.6–1.2 m → a door cut into that wall;
  ≥ 3 parallel strokes inside a wall band over ≥ 0.4 m → window. The rules move into this module; their tests stay.
- real01 expected (reference D1–D5, W1–W9, O1/O3/O5): 5 doors (two on the split run gap at x 11.0 ft, the bath door
  and the store door on extended walls, the entrance on a run gap), 9 windows, 3 doorless openings.

### 2.7 Rooms (`generic/topology.py`, `generic/labels.py`, `rooms.py`)

#### 2.7.1 Faces and virtual separators
- Faces = holes of the building wall union with every opening bridged (as today). `rooms.derive_rooms` gains
  `union=None` (a ready geometry) and `separators=()`; the old call keeps working; unlabelled faces get the placeholder
  label of §1.3.
- **Separator candidates** (method `derived`, evidence = the wall ids), only from free ends whose end gap was empty:
  *end-to-wall* (the empty end gap itself, ≤ 2.4 m) and *end-to-end* (two free ends of parallel walls whose end faces lie
  within 0.20 m of one line perpendicular to them, ≤ 2.4 m apart).
- A candidate is **kept** only if a face holding ≥ 2 room-name blocks gets fewer per face, or it separates a stair (§2.8)
  from a labelled face. Kept → `OpeningItem` `type "opening"`, `virtual true`, `wall_id null`, `line`; dropped ones are
  listed ("considered, not needed"). A face still holding ≥ 2 names → first name, `unverified`, conflict (as today).
- Unlabelled faces: `hall` when they touch ≥ 2 doors/openings, else `unknown`; a face holding a stair → `hall` with the
  stair piece; always `unverified`.
- real01 expected: 1 separator (dining wall free end → kitchen wall face, 1.29 m, reference O2); the lobby and the stair
  space form **one** unlabelled hall 5'0" × 15'0" behind the 6'0" doorless opening (reference `circulation.merged_face`;
  the two-space reading is also accepted by the test).

#### 2.7.2 Labels and vocabulary
- **Label blocks**: runs stacked (vertical gap ≤ 0.8 × line height, horizontal overlap ≥ 30 %) or a run ending in
  `+`/`&`/`-` are one block (`Bath+` + `Toilet` → `Bath+ Toilet`); a last line that is a size pair or an area →
  `label_size` / area label. Anchor = centre of the name line.
- **Room-name vocabulary** (English, case-insensitive, word start; Turkish unchanged):

| Type | Keywords |
|---|---|
| living | drawing, living, lounge, family, sitting; `hall` alone only when the face ≥ 9 m² and aspect ≤ 2.5 (else `hall`) |
| dining | dining |
| bedroom | bed room, bedroom, master, guest room, kids, children, nursery, br |
| kitchen | kitchen, kit, pantry |
| bathroom | bath, bathroom, shower; a bath/shower word with toilet/wc → bathroom |
| wc | toilet, wc, w.c, powder (no bath/shower word) |
| hall | lobby, passage, corridor, foyer, entrance, entry, landing |
| balcony | balcony, terrace, deck, verandah, veranda |
| storage | store, storage, closet, box room |
| prayer | pooja, puja, prayer, mandir |
| other | study, office, utility, laundry, servant, maid |
| *exterior* (site, not a room) | parking, car porch, porch, garden, lawn, sit out, sit-out, setback, otla, court, courtyard, drive, gate |

#### 2.7.3 Size and area labels
`label_size` (w, l) vs the face's clear size (minimum-area rectangle, both orientations): `ok` when both sides are within
max(5 %, 0.15 m); `conflict` beyond (`label_size_mismatch`; the room `unverified` beyond 10 %); `unchecked` when the face
is not rectangular (area / rectangle < 0.9) — then w·l vs the face area at 8 %. Area labels in sq ft use `_check_areas`
with the unit-aware parser.

### 2.8 Furniture (`generic/symbols.py`, G2)

- **Strokes considered**: inside the building outline; polylines and closed paths are first **split into segments**; a
  segment is dropped as wall outline when ≥ 90 % of its length lies within 20 mm of the bridged wall geometry (wall
  rectangles plus every opening rectangle); also dropped: wall primitives, strokes owned by openings (§2.6), dimension
  strokes, separator lines, glyph strokes inside text boxes (grown 10 %).
- **Chaining**: straight strokes whose ends meet within 5 mm are chained into polylines (real01's counter is 4 lines).
- **Clusters**: union-find over strokes closer than 20 mm (dots included); a cluster whose bbox lies ≥ 80 % inside another
  is merged into it **unless** it is a closed polygon with both sides ≥ 0.3 m that fits a size-table type (a sink or hob
  in a counter stays its own piece).
- **Composite split**: a cluster that fits no size-table type, or that holds ≥ 2 top-level closed contours ≥ 0.20 m
  (from polygonizing its segments; contours overlapping < 15 % of the smaller), is split: each top-level contour plus
  the strokes inside it seeds one piece; remaining strokes are re-clustered at 2 mm after the seed rings are removed
  and attach to the seed whose polygon contains them or whose ring is nearest within 20 mm; edge contact between pieces
  never merges them. Parts that fit no type and cannot be split stay **one composite**: `unknown`, `unverified`, note
  "possible group of N pieces", never typed as one table or bed. real01 target: 2 beds, 4 nightstands, 1 table, 6 chairs;
  if the rule cannot separate a group, the test accepts the composite as `unknown`/`unverified` for that group and the
  report lists it.
- Clusters with both sides < 0.20 m are details (counted, dropped); > 4.5 m on a side → `unknown`, `unverified`.
- **Footprint**: minimum-area rectangle snapped to the dominant orientation within 3°; `center`, `size` [width, depth]
  (width = longer side unless a front fixes it), `rotation_deg`; evidence `vector`, entity = stroke ids (ranges),
  `pixel_box`, confidence 0.9.
- **Deterministic types**:
  - *stair*: merge collinear overlapping strokes (same line within 5 mm, union extent); split tread strokes at a
    perpendicular stroke crossing ≥ 80 % of them; each side with ≥ 5 equal, evenly spaced (0.20–0.35 m ± 10 %) segments
    is a flight; type `stair`, `type_method "rule"`, footprint `verified`; flights, turn and direction recorded with
    `turn_assumed`, `direction_assumed` true and the reason. real01: 2 flights of 0.762 m with 8 lines each (0.253 m),
    x 11.25–13.75' and 13.75–16.26', y 15.26–21.09', landing 0.66 m. A rule stair in a face that is neither hall nor
    unlabelled → `unverified` + warning.
  - *kitchen counter*: a chained polyline of ≥ 2 straight legs whose two ends lie within 50 mm of a wall face (openings
    included) and that runs parallel to walls at 0.45–0.75 m → one `kitchen_counter` per leg (the corner square goes
    to the longer leg), front away from the wall, `verified` in a kitchen, else `unverified`. real01: 2.568 × 0.612 m
    and 0.609 × 0.992 m (reference F18a/F18b).
  - *block name* (DXF): keyword table (`BED`, `SOFA`, `CHAIR`, `TABLE`, `DINING`, `WC`, `TOILET`, `BASIN`, `SINK`,
    `WARDROBE`, `FRIDGE`, `STOVE`/`HOB`, `BATH`, `SHOWER`, `DESK`, `TV`, `PLANT`, `LAMP`, Turkish from `blocks.py`) →
    `type_method "block_name"`, confidence 0.9, checked against the size table.
  - everything else → AI **candidate** (§3): in the building as `type "unknown"`, `unverified`, `type_method "none"`
    until answers exist.
- **Front**: the side within 0.25 m of a wall is the back when it is the only such side; a bed's head = the side with
  ≥ 2 small closed shapes (pillows); a chair's back faces away from the nearest table. A unique deterministic candidate
  is kept when a pass names a side, also when an AI pass names another side (CLAUDE.md trust order: vector > AI; the
  disagreement is a `symbol_front_disagreement` conflict; changed after pod B, where both models named one fixed side
  for every bed and the old rule built real01's south bed reversed); with no deterministic candidate both passes must
  agree; else `front_deg null`.

### 2.9 Report and debug image (G3)

`report.md`: `Units`, the scale table (dimensions and size labels with ratios), `Site`, `Separators` (kept/dropped),
size-label checks, gaps (kind, class, owner strokes), furniture (type method, candidates, composites), `Assumed values`
(generated from the `assumed`/`label_source`/`stair.*_assumed` fields), lengths in the project's system (metres in
brackets). Debug image (150 dpi page render): wall mask, wall centre lines by method/confidence, doors (arc), windows,
doorless (dashed), separators (dashed magenta), rooms with label and type, furniture coloured by `type_method` (rule
green, block_name blue, ai_two_pass cyan, none red striped), site grey, scale dimensions orange. `_debug_items` uses
`evidence.method`.

### 2.10 real01 reference and acceptance (`tests/fixtures/real01_reference.yaml`, committed)

The reference (feet, origin = min corner of the house walls, X right, Y up) lists the scale (12.4352 pt/ft ± 0.2 %),
the L-shaped outline 42'6" × 24'0" with the parking notch, wall classes 6″/9″, 8 labelled rooms (2 Bed Room 11' × 10',
Drawing Room 14' × 14', Dining 14' × 8', Kitchen 9'3" × 10'3", Pooja 4' × 4'9", Store 4' × 5', Bath+ Toilet 7' × 5'),
the hall (one face or two spaces), doors D1–D5, windows W1–W9, openings O1–O5 (O2 separator, O4 optional), 20 furniture
pieces (2 `bed_double`, 4 `nightstand`, 1 `table_dining`, 6 `chair`, 2 `sofa`, 1 `table_coffee`, 1 round piece of open
type, 2 `kitchen_counter` legs, 1 `stair`), the site (plot wall 50' × 30', Parking, 9 plants, entrance step) and
per-element tolerances. Acceptance (`tests/test_real01.py`, CPU, `--no-ai`): status `ok`; scale within 0.2 %; every room
with type and label; doors and windows recall and precision 1.0 at the reference tolerances (≥ 0.9 is the floor);
doorless openings O1, O3, O5 and separator O2; every furniture footprint (or the documented composite fallback); rule
types correct; plot in `site`, nothing of it in `walls`; nothing built from `site`. With fake agreeing answers the AI
types are applied; with disagreeing answers they stay `unknown`/`unverified` with both candidates. Pod (§10): ≥ 80 % of
the AI-typed pieces get a reference-accepted type and no piece is `verified` with a wrong type.

## 3. Area Y – AI typing of unnamed symbols and raster room labels

### 3.1 Crops (`recognition/crops.py`)
Per candidate two 512 × 512 grey PNGs drawn with cv2 (§1.4): `<key>_ctx.png` — a square of side max(2.5 m, 1.6 × the
larger footprint side) around the candidate, walls mid-grey, other clusters light grey, the candidate black, a black
dashed box around it; `<key>_iso.png` — the candidate alone filling 80 %, with a 1 m bar (a filled bar, no digits). Keys
`sym_<level>_<n>`. Raster candidates use pixel crops of the rectified page with the same layout.

### 3.2 Size table (`recognition/size_table.yaml`)
Per type the plausible footprint range in metres (width × depth, either orientation, ± 15 % on top), for every
furniture type incl. the new ones; sources noted (standard furniture sizes; the synthetic block table; the real01
reference). Used by the core (block names, rules, composite split) and the two-pass rule.

### 3.3 Symbol question and the two-pass rule
- Prompt (both models, temperature 0, JSON schema): "Two crops of an architectural floor plan seen from above. The
  dashed box in the first image (shown alone in the second, with a 1 m bar) marks one drawn object. Which object type is
  it?" Schema `{"type": enum(furniture types ∪ {"not_furniture"}), "front": enum("top","right","bottom","left","none"),
  "confidence": 0..1, "reason": ≤ 160 chars}`. *Changed after the first prep pod (3 Oct 2026: 4 of 17 real01 pieces
  typed with the full list and no context):* the question states what the drawing shows — the drawn footprint size,
  for vector pages the room's printed label and type, and the neighbours (how many similar objects, the larger object
  they stand around or within 0.3 m of) — and offers only the types whose size range fits the footprint (+15 %) plus
  `unknown` and `not_furniture`; the schema's `type` enum is narrowed the same way. It says that small symbols drawn
  on top of an object (lamp, telephone, vase, plant, pillows, books) belong to that object, and defines the front in
  image terms (bed: the foot end; seating: the open seat edge; cabinets and appliances: the door/drawer side; counter,
  desk, washbasin, toilet, bathtub: where the user stands or sits; none for front-less objects). Raster crops get
  their own image description (dark ink, text may appear and is ignored). These facts are part of `input_sha256`.
  Raster questions carry no room label or neighbours (they can change with the same round's label answers).
- Pass 1 = Qwen3-VL-8B, pass 2 = GLM-4.6V-Flash (`check.yaml models`, pinned revisions).
- **Rule**: T accepted (`type_method "ai_two_pass"`, `verified`, evidence: vector footprint + two `ai` entries,
  confidence = min, capped 0.9) only when both passes say T and the footprint fits T's size range. Otherwise `unknown`,
  `unverified`, `type_candidates` = both answers, conflict `symbol_type_disagreement`. Both `not_furniture` → kept as
  `unknown`, `unverified`, `build: false` (an obstacle for the placer, not rendered; the room keeps
  `has_documented_furniture`), reported "drawn symbol, not built". A type not allowed in the room (`ALLOWED_TYPES` +
  `side_table`, `floor_lamp`, `potted_plant` everywhere, `stair` in halls) → kept, `unverified`, warning.
- Both passes answer front `none` while the drawing gives one front (pillows, wall) → the drawn front is kept,
  `front_assumed` with the rule named; a typed piece without a front is oriented by its type's width/depth range,
  with a warning.
- Rule-typed `stair`/`kitchen_counter` and block-name pieces are never asked.

### 3.4 Raster room labels (`recognition/room_labels.py`)
One `room_label` request per room face of a raster page that has a scale (face crop grown by 0.5 m, 768 px). Schema
`{"label": str|null, "size_text": str|null, "area_text": str|null, "box": [x0,y0,x1,y1] on 0..1000 | null}`. **One rule
for every field**: accepted when both passes give the same normalised value (casefold, Turkish-aware, spaces collapsed;
null/"" never agree) **or** one pass equals the Tesseract text read inside the face; else null, both candidates listed,
room `unverified`. Size and area texts count for scale corroboration only after passing this rule. Accepted label boxes
are blanked before the final clustering (S).

## 4. Area S – raster adapter (wave 2)

### 4.1 Input, rectification, page frame (`rectify.py`, `raster.py`)
- Inputs: `.png`, `.jpg`, `.jpeg`, `.tif`; raster-only PDF pages rendered at 200 dpi (verified pixel size).
- Photo: page quad (largest 4-point contour ≥ 30 % of the image) → homography; the rectified aspect is the quad's ratio
  **snapped** to a standard sheet ratio (ISO √2, ANSI 1.294/1.545, ARCH 1.333/1.5) when within 4 % (`assumed`, reported);
  otherwise solved from the horizontal and vertical dimension groups separately (each ≥ 2 within 1 %); else
  `needs_review` ("photo aspect unknown"). No quad → `needs_review` for that page unless another page of the level
  exists (then evidence only).
- Scans: deskew by the dominant long-stroke direction (≤ 5°).
- The rectified image is written to `<out>/rectified/<file>_p<n>.png`; the page entry records `rectified_image` and
  `to_original` (3 × 3); `transform_to_building` maps rectified pixels (y flipped) to metres, so `debug_image` and
  `vision_check.plan_crop` draw on the rectified image with the same affine code as PDFs.
- Debug image per raster page: drawn on the **original** image through `to_original` (+ `_rectified.png`), walls and
  openings coloured by `raster` and confidence, labels by acceptance path, page quad drawn.

### 4.2 Wall mask and strokes
- Dark mask = adaptive threshold (block 51 px, C 10) ∪ Otsu.
- **Text removal**: Tesseract (eng+tur, psm 11, at 0° and 90°) boxes are blanked only when conf ≥ 60, the text matches
  the vocabulary, a number or a size pattern, and the height is 0.5–2 × the median text height; remaining glyphs go by a
  character-component filter (components ≤ 40 px, aspect ≤ 3, ≥ 3 aligned, not touching a wall band); accepted VLM label
  boxes are blanked before the final clustering.
- **Dimension lines** are found first (§2.3 finder on raster strokes) and removed with their ticks and extension lines.
- **Filled walls**: opening with `k = max(3, round(0.6 × t_min))` px (`t_min` = lowest distance-transform mode ≥ 3 px,
  × 2); closed thin rings enclosing < 2 m² and components not connected to an elongated one are dropped.
- **Outline walls**: pairs of long parallel segments (≥ 3 px apart, ≤ 0.50 m at the scale) with ≥ 70 % overlap; seeded
  from the outermost closed band loop and grown: a band is accepted only when both its ends land on accepted bands; a
  pair is rejected when a line is a side of a closed 4-sided loop ≤ 3 m per side whose other sides are not wall bands, or
  when a third parallel line lies inside the band; fill from line centre to line centre.
- Skeleton by cv2 morphological thinning (no ximgproc, no scikit-image); straight segments merged collinear within 1 px;
  **arcs** by circle fit on skeleton chains (RANSAC, radius 2–8 × the outer wall thickness, sweep ≥ 50°) and filtered in
  metres by the core. The mask (`raster` 0.85) and strokes (`source "raster"`) go into the `GenericPage`; the core does
  openings and furniture (method `raster`, confidence 0.7).

### 4.3 Scale and texts on rasters
Tesseract at 0° and 90° (conf ≥ 85) gives the dimension texts; paired with raster dimension lines, ≥ 3 ratios within 1 %
→ `dimension_text`, evidence `ocr` (the §2.3 rules otherwise). No readable dimensions → `needs_review` ("no dimension
readable on the raster page") — VLM texts never create a raster scale in M7. Room labels: §3.4.

### 4.4 Targets (CPU tests with fake/saved answers; pod with real ones)

| Page | Walls F1 (centre ≤ 0.10 m, thickness ≤ 0.05 m) | Openings recall (kind + centre ≤ 0.20 m) | Furniture footprint recall (centre, size ≤ 0.15 m) | Rooms with right label | Scale error |
|---|---|---|---|---|---|
| synthetic-02 scan | ≥ 0.9 (mask IoU ≥ 0.85) | ≥ 0.8 (incl. the outer-wall door d_L0_001) | ≥ 0.8 | 5/5 (pod) | ≤ 2 % |
| synthetic-02 photo | ≥ 0.8 | ≥ 0.7 | ≥ 0.7 | 5/5 (pod) | ≤ 3 % (x/y px/m within 0.5 %) |
| real01 scan (generated: 150 dpi, ±1.5°, noise σ 4, blur σ 0.7) | ≥ 0.9 vs the vector result | ≥ 0.8 | ≥ 0.8 | ≥ 7/8 (pod) | ≤ 2 % |
| real01 photo (generated like synthetic-02's) | ≥ 0.8 | ≥ 0.7 | ≥ 0.7 | ≥ 7/8 (pod) | ≤ 3 % |

synthetic-02 becomes a normal project (end state `ok` on the pod when the targets hold); its truth is regenerated with
walls/openings/footprints `raster`, types `ai`, scale `dimension_text` from `ocr`. synthetic-01's `1_kat_scan.png` is
evidence only (no requests; door/window/labelled-room counts compared ± 1); synthetic-01 still exits 0 with conflicts
equal to its truth. The real01 raster fixtures are committed as one-page projects under
`tests/fixtures/real01_raster/{real01-scan,real01-photo}/` (≤ 1.5 MB each).

## 5. Area D – DWG and the generic DXF adapter

### 5.1 LibreDWG
- `pod_setup_recognition.sh` part `libredwg`: clone tag `0.14` into `/opt/wenart/build/libredwg` (container disk), verify
  `git rev-parse HEAD` = d9468ae…, `git submodule update --init --depth 1 jsmn`, `cmake -G Ninja
  -DCMAKE_BUILD_TYPE=Release -DDISABLE_WERROR=ON -DENABLE_LTO=OFF -DBUILD_SHARED_LIBS=OFF`, `ninja dwg2dxf dwgread
  dxf2dwg`; install the three static binaries and `VERSION` ("0.14 d9468ae") into `/workspace/tools/libredwg/bin`; on
  reuse check that `dwg2dxf --help` runs. apt adds `cmake ninja-build`. `full.sh` and `prep.sh` setups ask for the part.
- `scripts/cloud-setup.sh` builds the same into `~/.cache/wenart/libredwg/bin` when git and cmake exist (≈ 3 min).
- `dwg.py`: binary from `WENART_LIBREDWG_BIN`, then `/workspace/tools/libredwg/bin`, then `~/.cache/wenart/libredwg/bin`,
  then `PATH`; `dwg2dxf -y -o <out>/converted/<stem>.dxf <in>` (**no `--as`**); `out_dir` required; audit with
  `ezdxf.recover` (errors → the file's elements `unverified`); **0 modelspace entities → `ConversionError` →
  `needs_review`**; per-type entity counts and the source `$ACADVER` recorded in `documents[]`; version from `VERSION`.
  ezdwg removed from the chain.
- Intake/report texts: "DWG is read with LibreDWG 0.14 (beta); if it fails, export DXF".

### 5.2 Generic DXF adapter (`dxf_generic.py`)
- Used when the DXF has none of the synthetic layers (`DUVAR`, `KAPI`, `PENCERE`, `MOBILYA`). Modelspace entities with
  INSERTs exploded recursively (`virtual_entities`, transforms applied, the block-name chain kept): LINE,
  LWPOLYLINE/POLYLINE (bulges → arcs), ARC, CIRCLE, ELLIPSE, SPLINE (flattened ≤ 5 mm), **HATCH as one shape with
  even-odd fill over all its paths** (`ezdxf.path.from_hatch`, hatch_style honoured), SOLID, TEXT/MTEXT (`\P` → runs),
  **INSERT ATTRIBs** (nested included, transformed), DIMENSION → `DimensionPrim` **measured from geometry** (aligned:
  |p2 − p1|; rotated: projection on `dxf.angle`, else on the dimension line of its `*D` block; reuse
  `dxf_extract._linear_dimension_span`; never code 42; ≤ 1e-6 → dropped with a warning). Colours: ACI resolved
  (BYLAYER), **ACI 7 and true-colour white → black**. Units: `$INSUNITS` (1 in, 2 ft, 4 mm, 5 cm, 6 m); 0 → resolved by
  the scale rules from the dimensions, none → `needs_review`. Wall-hint layers: names matching
  `WALL|DUVAR|A-WALL|MUR|PARED`.
- `collect_texts(doc) -> list[TextRun]` (modelspace TEXT/MTEXT, block texts, ATTRIBs) for classification (§2.1).
- **synthetic-06** (2+1 flat drawn "the real way"): layers `A-WALL` (one SOLID HATCH with the outer loop and room islands,
  ACI 7), `A-DOOR`, `A-GLAZ`, `A-FURN`, `A-ANNO`, `A-DIMS`; inches (`$INSUNITS=1`); blocks `BED-DOUBLE`, `SOFA-3`,
  `DINING-6`, `WC`, `BASIN`, `CHAIR`; one ROOMTAG block with an ATTRIB label; MTEXT labels `LIVING ROOM` + `14'-0" X
  12'-0"`; feet-inch dimensions (vertical ones as aligned dimensions, plus one rotated dimension to test the recovery);
  one open kitchen; **no title** (an untitled variant is the project; a titled variant is a test fixture). The project
  folder holds **only the DWG at top level** (`synthetic-06.dwg`, written by `dxf2dwg` R2000/ANSI_1252, deterministic,
  sha256 committed) and its DXF in `projects/synthetic-06/source/` (not read by the pipeline); truth from the generator.
  Tests: with a LibreDWG binary present (session build), the DWG run equals the DXF run (paths and converter strings
  aside, `DimensionPrim` lists equal) and matches the truth — this test must pass, not skip, before §12; without the
  binary the synthetic-06 pipeline tests skip. The full run on the pod exercises the DWG path.

## 6. Area L – look, cameras, library filter, Blender

### 6.1 AgX Punchy
`render.py`: `LOOK = "AgX - Punchy"`, `RENDER_CODE_VERSION = "m7.1"`, `view_transform` and `look` in `key_settings`;
`window_pull` passes the look to `save_display`. (`stages.ALT_LOOK = "None"` and its pins: R.) EV and white balance are
metered scene-linear and do not change.

### 6.2 Views
`camsearch.plan_room`: rooms whose `RoomModel.pieces` (furniture after layout and decor, without decor and without
`build: false` pieces) is empty get `EMPTY_ROOM_VIEWS = 1`; such rooms with area < `MIN_EMPTY_ROOM_AREA_M2 = 2.5` get 0
views and the scene manifest lists them under `rooms_without_view` with the reason. (`plan.py`'s pre-layout estimate: R.)

### 6.3 Library style filter
- `style/profile.py` writes `family` (from `STYLE_FAMILIES`, `null` when none matched; defaults.yaml profile and Blender's
  `BUILTIN_DEFAULTS` mirror updated).
- Catalog entries get `styles` (families or `neutral`), `style_note`, and for beds `has_mattress`; the 31 Poly Haven
  models are tagged from the Poly Haven API tags and thumbnails (reason in `style_note`); `GothicBed_01`,
  `GothicCommode_01` → `classic`; `old_bed_frame` removed (no mattress; `bed_single` becomes parametric until O adds one).
- `fit_piece(piece, catalog, style_family=None, …)`: candidates whose `styles` contain the family or `neutral` (all when
  the family is null); none → parametric with reason `no model for style <family>`. **Only `refit` gets `--style
  <out>/style.json`** (it runs after the final style); `fit` stays style-free (R adds style.json and
  `catalog_objaverse.json` to refit's fingerprint inputs).
- `catalog.validate` accepts `source ∈ {polyhaven, objaverse}`, `licence ∈ {CC0, CC-BY-4.0}`; a CC-BY entry needs
  `title`, `author`, `source_url`, `licence_url`, `via`, `attribution`.
- Licence gates (`assets/fetch.py`, `assets/models.py`, `blender/furniture.py`): models CC0 or CC-BY-4.0 with
  attribution; textures and HDRIs CC0 only; `load_manifest` checks each entry against its kind's rule.
- `models.fetch_model(..., source="objaverse")` reads only the cache `/workspace/assets/models/objaverse/<uid>.glb`
  (written by the prep pod, sha256 from the catalog); a miss → warning and parametric (full runs are offline).

### 6.4 New parametric types and geometry
- `stair`: flights and landing as drawn; each drawn tread line is a nosing, so a flight with n lines has n risers; riser height = (ceiling height + assumed slab 0.15 m) / total
  risers, recorded `riser_source "derived from assumed ceiling and slab"`, warning outside 0.15–0.20 m; drawn steps are
  never added or dropped; direction: away from the flight end facing the hall's open side (`direction_assumed`); the
  ceiling opening covers the last flight + landing only (`void_assumed`) and is closed by a neutral shaft cap 0.5 m above
  the ceiling so nothing unmodelled is visible; a simple handrail on the free side (`assumed`). Unknown direction →
  steps rise along +local Y, recorded.
- `side_table` (round when a circle fits ≥ 90 % of its points), `floor_lamp` (base, pole, fabric shade; no light),
  `potted_plant` (the decor plant model scaled to the footprint). `build: false` pieces are not built.
- Doorless openings: cut to `height` (2.10 `assumed`), no frame, no leaf. Virtual separators: no geometry; floors and
  ceilings meet at the line. Site elements are not built.
- `dining` and `prayer` rooms use the living slots; `prayer` gets no decor.

### 6.5 Layout, decor, words
`ALLOWED_TYPES["dining"] = ("table_dining", "chair", "dresser", "bookshelf")`, anchor `table_dining`; `prayer` not
furnishable. `side_table`, `floor_lamp`, `potted_plant`, `stair` are documented-only: they get `SIZE_OPTIONS`/`HEIGHTS`
entries for the fit and the placer but are excluded from `LAYOUT_TYPES` (`test_layout.py:202` updated to "every schema
type except the documented-only ones"). `furniture/prompts.py` gets `ROOM_TYPE_TEXT`/`ROOM_GUIDE` for dining (and a
prayer entry for completeness); `polish/prompt.py` `ROOM_WORDS`/`FURNITURE_WORDS` cover the new types.

### 6.6 Interface to O
`catalog.load()` merges `wenart/furniture/catalog_objaverse.json` (absent → nothing) after `catalog.json`; both pass
`validate`. Objaverse entries carry the frame fields (`front_axis`, `bbox_m`, …) plus `glb`, `sha256_glb`, `uid`,
`title`, `author`, `source_url`, `licence`, `licence_url`, `via`, `attribution`, `styles`, `has_mattress`.

## 7. Area O – Objaverse library (prep pod)

### 7.1 Survey (`python -m wenart.assets.objaverse survey --cache /opt/wenart/hf --out $RESULTS/library`)
1. Download `lvis-annotations.json.gz`, `object-paths.json.gz` and the metadata shards of the candidate uids into the
   container-disk HF cache (never in the session; before `HF_HUB_OFFLINE` is set).
2. LVIS categories → types (`objaverse.yaml`, names verified against the downloaded file): `bed` → bed_double/bed_single
   by size, `sofa`, `armchair`, `dining_table`, `coffee_table`, `bookcase` → bookshelf, `wardrobe`/`armoire`,
   `nightstand`, `chest_of_drawers_(furniture)` → dresser, `desk`, `toilet`, `sink` → washbasin, `bathtub`,
   `refrigerator` → fridge, `stove`, `lamp` → floor_lamp (by height), `flowerpot` → potted_plant. No category for
   `tv_unit`, `kitchen_counter`, built-in wardrobes: parametric.
3. Licence from the metadata: only CC0 and CC-BY 4.0 (exact strings verified and written to `objaverse.yaml`); NC, ND,
   SA, "free standard", unknown → refused.
4. Prefilter: face count 2k–150k, ≤ 40 MB, textured or vertex-coloured; rank by `likeCount`, then `viewCount`;
   **≤ 8 candidates per type** (≈ 150 GLBs).

### 7.2 Thumbnails and judging (GPU)
- One Blender process (Cycles GPU, 16 spp, 256 px), 4 views per object (front, 45°, side, top) of the GLB normalised to its
  bbox; unit guess (× 1, 0.01, 0.0254, 0.001; the one in the type's size range). *Changed after the first prep pod
  (86 of 127 candidates fitted no standard factor):* when none fits, the model's units are unknown and the scale is
  normalised by type (`unit_scale` = the type's typical footprint / the raw footprint, `unit_note` "normalised by
  type (model units unknown)"); the proportions decide refusal (footprint w/d and height/width must fit the type).
  The fit scales every model to the drawn footprint anyway.
- Two VLM passes on a 2 × 2 sheet, inside the prep pod's Qwen and GLM sessions: `{"is_single_object", "matches_type",
  "photoreal_quality": 1..5, "has_mattress": bool|null, "styles": [family enum ∪ neutral], "front_view": 0..3|null}`.
- Accept: both `is_single_object` and `matches_type`; both quality ≥ 4; beds both `has_mattress`; bbox aspect in range;
  for every type with a front (all except table_dining, table_coffee, side_table, potted_plant, floor_lamp) both passes
  give the same `front_view` **and** it matches the geometric check used for Poly Haven (taller side = back for seating
  and beds; door/drawer side = front for cabinets), else refused "front not agreed"; `front_axis_confidence: low` only for
  front-less types; `styles` = intersection of the two answers (`neutral` counts only if both list it), empty → refused.
- Output in `$RESULTS/library/`: `catalog_objaverse.json` (≤ 6 per type), thumbnails `<type>/<uid>.jpg` (256 px),
  `library_report.md` (counts, refusals by reason, attribution list), all with the ODC-By notice; the accepted GLBs are
  copied to `/workspace/assets/models/objaverse/<uid>.glb` on the volume. The integrator commits
  `catalog_objaverse.json` into `wenart/furniture/` between the prep pod and the full runs.

### 7.3 Licences and credits
Attribution line: `"<title>" by <author> (<source_url>), CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), via
Objaverse (allenai/objaverse, ODC-By 1.0); changes: scaled to the drawn footprint, re-oriented, rendered, AI-retouched`.
R's copy step writes `ATTRIBUTION.md` (the CC-BY assets used by that project) into every results folder that receives
images of a project (`renders`, `polish`, `gate`, `check`, `realism`, `final`) and into `results/library/`;
`catalog_objaverse.json` and `library_report.md` carry the ODC-By notice (this file is ODC-By, not MIT; README notes it).
Fewer than one accepted model for a (type, family) → parametric, reported.

## 8. Area V – added-object detection and realism v2

### 8.1 Detector (`wenart/gate/detect.py`, venv-polish)
- OWLv2 `google/owlv2-base-patch16-ensemble` @ `cfd3195ba4ea9592eec887ded089f4c08eff231d` (Apache-2.0) as `detect` in
  `gate/models.yaml` (`tests/test_m5_config.py` pins updated) and in `pod_setup_polish.sh part_models` (R).
- Query groups (plain words): one per furniture type, plus door, window, lamp, potted plant (→ decor class: never rejects,
  as today), picture frame, rug, vase, cushion, mirror, television. Images at 960 px long side.
- `python -m wenart.gate detect <out> --manifest <out>/polish/polish_manifest.json --out <out>/detect/` (phase 6, R):
  boxes per query for the Cycles image and the **chosen polish attempt** of each view → `detect/<cam>.json`; skip
  `polish off`, `smoke profile`, `gate not validated`.
- `python -m wenart.gate detect-calibrate --pairs <list.json> --out <dir>`: positives = M6 insertion controls (normal
  render as "polished", hide render as "Cycles"; 29 pairs on the volume: `outputs/synthetic-0{1,3,4,5}/controls/hide_*`
  with their M6 normal renders), negatives = M6 accepted polishes vs their Cycles images and benign perturbations (JPEG
  q70, noise σ 2, blur σ 0.6). Output `detector_calibration.json` with `t_det`, `t_strong`, rates; targets: insertion
  confirmed ≥ 60 %, false confirmed ≤ 3 %. The integrator copies the result into `check.yaml detector:` between the prep
  pod and the full runs; with no `detector:` block the detector is advisory and never rejects.
- **Decision in `vision_check combine` (phase 10)**: an *added object* = a polished box (score ≥ `t_det`) with no Cycles
  box of the same group at IoU ≥ 0.3 and not covered ≥ 50 % by an expected element of a compatible type (`coverage_map`);
  **confirmed** when score ≥ `t_strong` or a VLM extra of either pass overlaps it at IoU ≥ 0.3. A confirmed added
  non-decor object sets `added_by_polish` for that view in `check_manifest.json`; the report then uses the Cycles image.
  `combine_extras`: a single-pass VLM extra confirmed by a detector box counts as confirmed. The per-run insertion controls
  (`--kinds cycles,polished,controls`) record rates only.

### 8.2 Realism v2 (`vision_check/realism.py`)
- One call per (pair, aspect, order, model); four aspect prompts (template below); schema `{"winner": enum,
  "confidence"}`; for `order ab` the question names "Image 1 … Image 2" and the enum is `[image_1, image_2]`, for `ba`
  "Image 2 … Image 1" and `[image_2, image_1]`.
- Keys `realism2|<set>:<cam>|<aspect>|<order>`; answers in `check/realism/answers_realism2_<slug>.json`;
  `input_sha256` hashes the per-call prompt. Commands `realism2-pairs` (writes `ab/pairs_v2.json`, never reuses the M6
  file), `realism2`, `realism2-combine` (`realism2_ab.json`), `realism2-summary` (`realism2_summary.json`).
- Sets: `ctl_*` (4) and `null_identical`, `null_reencode`, `nuisance_ev` on 8 views from synthetic-01's M6 `ab/ctl_*`
  renders on the volume (`AB_CONTROL_PROJECT=synthetic-01`); `look_alt` = `renders/<cam>_preview.jpg` (A, Punchy) vs
  `renders/<cam>_alt_preview.jpg` (B, None) on 32 cameras of the AB projects (rank by furniture share, ≤ 2 per room,
  round-robin over projects). No `m5_vs_m6`. `null_identical` asked with 1 worker.
- Signal, decision, halo and position-bias rules unchanged (computed over the per-aspect calls).
- `tests/test_realism_ab.py` checks the template below verbatim (this section's code block).

```text
Look at the two images. Both show the same interior from the same camera.
Question: which image looks more like a real photograph in its {aspect_name}? Compare {first_image} with {second_image}.
Judge only {aspect_name}: {aspect_cues}
Answer with the image whose {aspect_name} is more photographic. There is no tie.
```
(`first_image`/`second_image` = "Image 1"/"Image 2" for `ab`, swapped for `ba`; materials — "surface texture, reflections,
wear, believable material scale"; lighting — "light falloff, soft shadows, window light, no flat fill"; furniture —
"proportions, contact with the floor, soft goods, believable detail"; photo — "the image as a whole: camera, exposure,
colour, absence of render artefacts".)

## 9. Area R – orchestrator, prep job, runner, report (wave 2)

### 9.1 Stages, phases, states
- New project stages (numbers re-assigned contiguously; `tests/test_run_stages.py` pins the new table): `recognize`
  (after `pipeline`; GLM pass in phase 2, Qwen pass in phase 3; `on_failure warning`; reuse by answer keys;
  `--seed-answers results/recognition/<p>/`), `pipeline_final` (CPU, phase 3 after the Qwen answers; fingerprint inputs =
  building inputs + both answer files; records the canonical sha256 of the building.json it wrote and is reused only while
  it still matches; skipped `no questions` when the first pipeline exit was 0; unanswered keys → `--no-ai`, so it never
  exits 4), `detect` (phase 6, holder gate).
- `stage_pipeline` checks rc 4 first: status **`pending`** (added to `STATUSES`, `GOING_ON`, `REUSABLE`, severity ok), so a
  resume reuses it instead of overwriting the building; phase 1 skips fit for pending projects (fit runs after
  `pipeline_final`); a pending project with no `pipeline_final` record of this run ends `incomplete`; `REVIEW_STAGES` +=
  `pipeline_final`; `SKIP_REASONS` += `no questions`.
- Phase 2 (GLM) runs when photos **or** recognition questions are pending; phase 3 (Qwen): recognition, then
  `pipeline_final` and `fit` for those projects, then photos/restyle/layout as before. Server starts stay ≤ 4.
- refit fingerprint inputs += `style.json`, `wenart/furniture/catalog_objaverse.json`; refit gets `--style`.
- Pipeline fingerprint += the LibreDWG `VERSION` string. `stages.ALT_LOOK = "None"`; stage 10 render passes
  `--alt-look None` for projects in `--ab` (the alt preview comes from the same render result).
- Check: `--kinds cycles,polished,controls`. Phase 10: `combine` reads `detect/`. AB: `realism2-*` commands; cut
  detection and the phase-10 gate read `check/realism/answers_realism2_<slug>.json`; estimates count 8 calls per pair and
  64 single-worker calls for `null_identical`.
- vLLM: `server_seqs(mem) = min(check.yaml models.<k>.max_seqs, 8 if mem ≥ 80000 MiB else 4 if ≥ 40000 else 2)`;
  `server_args(8)` = `--max-model-len 32768 --max-num-seqs 8`. No runtime fallback.
- Smoke profile: `pipeline_final` runs with `--no-ai` (fake answers would agree); detector skipped. New needs_review
  fixture `tests/fixtures/projects/review-01` (two untitled plan pages: "cannot order untitled plan pages") replaces
  synthetic-02 as the e2e needs_review project and as the `PRIVATE_SELFTEST` source; `test_run_e2e` expected states and
  totals updated.
- Copy rules: `debug/*.png` of public projects (≤ 3 MB each), `rectified/*.png` (≤ 3 MB), `recognition/requests.json`,
  `recognition/answers_*.json`, `recognition/crops/*.png` (≤ 200 per project), `detect/*.json`; `ATTRIBUTION.md` per §7.3;
  `$RESULTS/library/**`, `$RESULTS/detect/**`, `$RESULTS/timing/**` from the prep job.
- `pod_requirements.txt` and `cloud-setup.sh` pin `matplotlib`, `opencv-python-headless`, `pillow`, `numpy` to the
  session's versions.

### 9.2 Prep job (`scripts/jobs/prep.sh`, `python -m wenart.run prep`)
Fixed order: setup (venvs, LibreDWG, HF downloads of Qwen, GLM, OWLv2, Objaverse metadata + candidates); library survey;
thumbnails (Blender GPU, no vLLM running); `detect-calibrate`; timings (render 10 views of synthetic-04 from its M6
`scene.blend` with the M7 render code, 4 polish attempts) → `$RESULTS/timing/gpu_speed.json`; Qwen session (8-seq probe →
`max_seqs`; recognition requests of real01, synthetic-02, synthetic-06 and the two raster fixtures — pipelines run with
`--outputs /workspace/outputs-prep`; library judging) then GLM session (same); `pipeline_final` for those projects;
answers to `$RESULTS/recognition/<p>/`; GPU tests `test_recognition.py`, `test_library.py`, `test_detect.py`.
**Between the prep pod and the full runs** the integrator commits: `wenart/furniture/catalog_objaverse.json`, the
`check.yaml detector:` block, `plan.GPU_SPEED`, `check.yaml models.<k>.max_seqs`, `results/recognition/<p>/` and the
answers of the raster fixtures into `tests/fixtures/recognition_answers/`.

### 9.3 Time rule (`plan.py`)
`GPU_SPEED = {"RTX PRO 4500": 1.0, "RTX 4090": 1.1, "RTX PRO 6000": <prep pod>}`, default 1.0, applied to the per-view and
per-project minutes and to `stages.EST_*`; `plan --gpu NAME` (default `GPU_PRIORITY[0]`); `server_starts(photos, layout,
questions)` gives 4 when questions are pending; a pipeline rc 4 → `pending` with time (views `unknown` for raster projects
without rooms, pod row marked not verified); window pull + 1 s per view; recognition calls × 2 models × `EST_VLM_CALL_S /
seqs`; the pre-layout view estimate uses §6.2's rule.

### 9.4 Report
Units per project; **side-by-side sheets** (Cycles left, polished right, gate and check decisions) per room for every
project with polish on (user decision 4: decide polish again after looking at real01); recognition section (AI-typed
pieces with both answers, composites, raster pages with acceptance paths), site, separators, assumed values;
attribution section; `NEEDS_REVIEW_HINTS` updated (DWG, raster: "no page quadrilateral", "no dimension readable",
"photo aspect unknown", "text drawn as geometry").

### 9.5 Runner
`GPU_PRIORITY` unchanged (RTX PRO 6000 first). `full.sh` header `--gpu 'RTX PRO 6000' --disk 150`
(`tests/test_full_job.py` follows); `RECOG_SETUP_PARTS` adds `libredwg` (`tests/test_polish_job.py:217` follows).

## 10. Pods and budget

Spent today (3 Oct, UTC) before M7: $2.66 of $10.00. RTX PRO 6000 $2.09/h, HIGH stock. Deadlines: `WENART_DEADLINE` =
start + max − 15 min.

| Pod | Content | Max min | Worst case | Day |
|---|---|---|---|---|
| prep | §9.2: setup 8, survey 5, thumbnails 12, detector calibration 3, timings 5, Qwen 5 + calls 6, GLM 3 + calls 5, pipeline_final 1, tests + copy 4 ≈ 57 min | 90 | $3.14 | 3 Oct |
| B | full run: **real01** first, synthetic-01, synthetic-04, synthetic-02, synthetic-06 (re-planned with the measured `GPU_SPEED`; a project that does not fit moves to pod C) | 115 | $4.01 | 3 Oct (2.66 + 3.14 + 4.01 = 9.81) |
| C | full run: synthetic-03, synthetic-05 (+ moved ones); AB `AB_PROJECTS='synthetic-03 synthetic-05' AB_CONTROL_PROJECT=synthetic-01 AB_PHASE=all` (≈ 704 calls per model) | 115 | $4.01 | 4 Oct |

Before the prep pod: CPU suite green here, the DWG real-binary test passing in the session, `python -m wenart.run plan`
for all projects, the smoke e2e. A cut pod resumes with the same command (on the next day if the daily cap requires).
Every pod is logged in `docs/gpu-log.md`; no pod left running; ask the user before any action over $5 or any limit change.

## 11. Tests (CPU unless marked)

- G1: units (every spelling, round trips, pairs, areas, ambiguity); label blocks and the vocabulary table (every row,
  `Bath+ Toilet`, `Kitchen & Dining`, `Living / Dining`, `Banyo/WC`, casing of `LIVING ROOM`); dimension finder
  (arrowheads, ticks, dots, extension lines, text in a vertical line's gap, real01's two); scale branches and the
  corroboration, raster scale-note rule (synthetic-02 scan with `1/100` read does **not** take the note).
- G2: hatch groups (spacing, angle, colour), dark-fill chroma rule, mask decomposition on L/T/+ (IoU ≥ 0.97), face
  snapping (real01 0.150/0.230 m), gaps of all three kinds and their classes (real01 5/5 doors incl. the extended
  walls, 9 windows, 3 doorless), exterior empty gap unverified, owned strokes; plot (C-shape by hull, other components,
  exterior faces inside the loop); separators (kept/dropped, only from empty end gaps); clusters (segment-wise outline
  removal: no cluster > 4.5 m on real01; containment exception; composite split on the real01 dining and bed groups);
  stair (dedupe, divider split, real01 2 flights); counter (chaining, faces incl. openings); fronts.
- G3: CAD-PDF adapter (y flip, Bézier from `path`: real01 gives 5 arcs r 0.72–1.02 m, colours, dots); classification
  (generic labels for PDF and DXF, L0 assumption, several untitled pages, SHX-text page → needs_review until S);
  `tests/test_real01.py` (§2.10); synthetic-01, -03, -04, -05 `test_matches_truth` unchanged.
- Y: crop determinism (canonical hash stable across PNG metadata), prompt/schema strictness, two-pass table (agree,
  disagree, size veto, not_furniture kept with `build: false`, room veto, empty never agrees), answer store and seeding,
  CLI exit codes with a fake server, pipeline exit 4 / `--answers` / `--no-ai`.
- S: rectification (corners ≤ 1 % of the side; x/y px/m within 0.5 % on the synthetic-02 photo), deskew + `to_original`
  (truth label boxes map back within 2 px), text blanking (no wall ink lost), dimension removal, both wall styles (scan mask
  IoU ≥ 0.85), arcs, the §4.4 targets with fake/saved answers, evidence-only pages (synthetic-01 exits 0, conflicts as
  truth), raster debug image on the original, a plan-crop point on the synthetic-02 photo at its truth pixel.
- D: dwg.py with a stand-in `dwg2dxf` (args without `--as`, version file, out dir, audit, empty modelspace →
  needs_review), with the session binary (synthetic-06 DWG = DXF, DimensionPrim lists equal); generic DXF (nested inserts,
  ATTRIBs, units 1/2/4/5/6/0, even-odd hatch with islands, ACI 7, dimension measurement incl. the rotated one);
  same-stem rule; synthetic-06 truth (untitled project, titled fixture).
- L: look constants and render key; empty-room views; style family; refit style filter; licence gates per kind; Objaverse
  cache-only fetch; stair (risers from drawn lines, void cap), side table, floor lamp, potted plant meshes (Blender, skip
  without it); doorless cut; separator without geometry; `build: false` not built; layout types; word tables.
- O: survey filters on canned metadata, licence strings, unit guess, accept rules (front agreement, style intersection),
  attribution lines, ODC-By notice.
- V: detector decision on canned boxes, calibration maths, combine with single-pass extras, plant stays decor, realism v2
  keys/prompts (verbatim §8.2)/enum alternation/outcomes/controls, `--kinds` includes controls.
- R: stage table, `pending` handling and resume, recognize/pipeline_final order, ≤ 4 server starts, 8-seq tier,
  plan golden output incl. real01 and `--gpu`, prep job static checks and order, copy rules incl. ATTRIBUTION.md,
  report sections, full.sh/prep.sh static checks, smoke e2e with review-01.
- GPU: `test_recognition.py` (answers complete; §4.4 targets; real01 AI typing ≥ 80 % and no wrong verified type),
  `test_library.py`, `test_detect.py` (calibration recorded), `test_full_run.py` (real01 and every RUN_TEST project `ok`;
  `pipeline` `pending` only with `pipeline_final` ok/reused), `test_render.py` (Punchy; empty rooms ≤ 1 view),
  `test_check.py` (insertion measured), `test_realism.py` (v2 summary).

## 12. Done criteria

CPU suite, smoke e2e and `wenart.run plan` green here; the DWG real-binary test passing in the session; prep, B and C exit
0 (resumed pods count); real01 `ok` end to end with side-by-side sheets and the §2.10 acceptance; synthetic-01…06 `ok`
(02 via the raster path, 06 via the DWG path); GPU tests green; detector calibration and realism v2 reported (whatever
they say); results committed under `results/`; docs updated: `docs/plan.md` §4.3 ("LibreDWG 0.14 (d9468ae), GPL-3.0,
built from source on the pod, called as a separate program, binaries never distributed; ezdwg dropped"), §4.8
("Objaverse 1.0 (HF allenai/objaverse @21e4e14) ODC-By 1.0; objects CC0/CC-BY 4.0 only; per-object licences are
uploader-declared and unverified — flag for commercial use"), §8 (Milestone 7 models: OWLv2 base-patch16-ensemble
Apache-2.0 @cfd3195; Grounding DINO / Florence-2 surveyed, not used; TRELLIS.2 not used), `docs/progress.md` (incl.
"needs your OK": TRELLIS.2, real01 style), `docs/gpu-log.md`, `docs/synthetic.md`, `docs/intake.md`; no pod running.

## 13. Risks

| Risk | Mitigation |
|---|---|
| Real plans vary far beyond real01 | every rule that fired is logged; anything not understood is `unverified` or a warning, drawn in the debug image |
| Separators split open plans differently from the architect | only where two names share a face; listed and drawn; size labels cross-check |
| Composite groups (bed + nightstands, table + chairs) not separable | the composite stays one `unknown`/`unverified` footprint, never mistyped |
| VLMs disagree on most symbols | per-piece crops at a readable scale; disagreement keeps the drawn footprint |
| Raster walls noisy on photos | photos secondary when a scan or vector exists; targets per page; failures → `needs_review` with the reason |
| LibreDWG 0.14 beta | audit, empty-modelspace check, entity counts; DXF export remains the fallback |
| Objaverse quality and licences | CC0/CC-BY only, two judges, fronts agreed, thumbnails committed, attribution everywhere |
| AgX Punchy breaks gate validation | every polished project is re-calibrated and validated; failure → Cycles finals |
| Pod B over time on the new GPU | prep pod measures `GPU_SPEED`; re-plan; move projects to pod C |
| real01 style is the default | reported as assumed; a user brief re-runs style → refit → build → render → polish → check |

## 14. Sources (checked 3 Oct 2026)

- LibreDWG tags via `git ls-remote https://github.com/LibreDWG/libredwg.git` (0.13.3, 0.13.4, 0.14 = d9468ae, nightly
  0.14.NNNN); static build and `--as` behaviour measured in the session.
- Hugging Face API: `allenai/objaverse` (21e4e142159e2153706c23a3a02e55cec5591cea, ODC-By 1.0);
  `google/owlv2-base-patch16-ensemble` (Apache-2.0, cfd3195ba4ea9592eec887ded089f4c08eff231d);
  `IDEA-Research/grounding-dino-base` (Apache-2.0, 12bdfa3120f3e7ec7b434d90674b3396eccf88eb);
  `microsoft/Florence-2-large` (MIT, 21a599d414c4d928c9032694c424fb94458e3594).
- CC BY 4.0 §3(a)(1); ODC-By 1.0 §4.2–4.3.
- RunPod `/v2/catalog/gpus` via `scripts/gpu_run.py gpus` (3 Oct 2026 06:40 UTC): RTX PRO 6000 96 GB $2.09/h HIGH.
- real01 and synthetic-02 measurements: pdfplumber 0.11.10, opencv 5.0.0, tesseract in the session; reviewer scratch.

## 15. Changes while running (3–4 Oct 2026)

| Found on | Change | Where |
|---|---|---|
| prep pod 1 | judge schema without `uniqueItems`; models of unknown units normalised by type (noted); LVIS names fixed; the symbol question gives the drawn size and room (question facts); one question round only | §3.3, §7.2, `wenart/assets/objaverse.py`, `wenart/recognition/` |
| prep pod 2 | real01-photo missed the bath and store doors: a short frame nub is not a wall end, a door leaf fused to a wall face joins its run when a swing explains it (P7) | §2.6, `generic/openings.py` |
| pod B | a unique drawn front outranks AI fronts; the disagreement is a `symbol_front_disagreement` conflict (real01's south bed was built reversed) | §2.8, `recognition/symbols.py` |
| pod B | the camera model builds pieces with a back (beds, chairs, sofas, armchairs, toilets) from the builder's parts (low part + back slab), not one full-height box | §6.2, `blender/camsearch.py` |
| pod B | the M5 e2e combines with the detector advisory (it has no detect stage); tests follow the committed real01 seeds | tests |
| pod C2 | an A/B project must be rendered in the same pod (or with the alternate look): synthetic-05 had no pairs | §10 (open) |
