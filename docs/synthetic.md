# Synthetic test projects (Milestone 2 §1, Milestone 6 §3)

Five generated projects with known ground truth, used to test the vector path
(`wenart/ingest`), the raster bake-off (`wenart/recognition`) and, from
Milestone 6, the one-command full runs (`wenart/run`): synthetic-01..03 were made
in Milestone 2, synthetic-04 and synthetic-05 in Milestone 6 (docs/milestone6.md §3).

```
python -m wenart.synthetic.generate --out projects --results results/synthetic
```

The command is deterministic and idempotent: fixed seeds, fixed DXF/PDF metadata,
byte-identical files on every run (`tests/test_synthetic.py::test_deterministic`
and `test_committed_projects_are_current` check this). After changing the
generator, run it again and commit `projects/` and `results/synthetic/`
(`--only synthetic-05` regenerates one project).

## The five projects

| Project | Documents | Levels / rooms | Furniture in documents | Brief | Deliberate conflicts |
|---|---|---|---|---|---|
| `synthetic-01` | `zemin_kat.dxf` (L0), `1_kat.pdf` (L1, vector), `1_kat_scan.png` (scan of the PDF) | L0: Salon 24,50 m², Mutfak, Yatak Odası, Banyo, Hol; L1: Ebeveyn Yatak Odası, Çocuk Odası, Hol, Yatak Odası, Banyo | L0 only, in Salon, Yatak Odası, Banyo (13 pieces) | `brief.yaml`: one `style` | none (the Salon label matches the polygon exactly) |
| `synthetic-02` | `plan_scan.png` (scan), `plan_photo.jpg` (phone photo). The source vector PDF is hidden in `truth/plan.pdf` | L0: Salon, Mutfak, Antre, Banyo, Yatak Odası (1+1 flat) | all rooms (19 pieces) | none (defaults) | none |
| `synthetic-03` | `kat_planlari.pdf` (3 pages: Bodrum, Zemin, 1. Kat), `mobilya_plani.dxf` (furniture plan of Zemin Kat: walls, openings, furniture, no dimensions) | L-1: Kiler ×2, Hol, Yatak Odası, WC, Banyo; L0: Salon, Mutfak, Antre, Hol, Yatak Odası, WC, Kiler; L1: Ebeveyn Yatak Odası, Çocuk Odası, Hol, Yatak Odası, Banyo, Balkon | L0 only, DXF only (21 pieces incl. one `BLOK_A` of unknown type) | `brief.yaml`: `styles: [two prompts]` | `c_001` Salon label 24,00 m² vs 23,50 m² computed (2 %, within tolerance); `c_002` Bodrum left dimension prints `3,99` for 3,80 m (5 %); `c_003` the PDF Zemin page lacks the Mutfak window that the DXF has (count mismatch, DXF wins) |
| `synthetic-04` | `3_kat_plani.dxf` and `3_kat_plani_pdf.pdf` (vector): the same level twice, both with walls, openings, furniture and dimensions | L3 (`3. KAT PLANI`, elevation 9.0): Salon + Mutfak 39,05 m² (L-shaped, 6 vertices), Hol (L-shaped, 8.32 m²), Yatak Odası, Banyo, Çocuk Odası (2+1 flat) | Salon + Mutfak, Yatak Odası, Banyo (21 pieces, each on both documents; the armchair at 45°; a `KUVET` bathtub); Hol and Çocuk Odası empty | `brief.yaml`: `style` (Japandi, walnut floor, cream walls) | none |
| `synthetic-05` | `zemin_kat.dxf` (floor plan: walls, openings, dimensions, **no furniture**), `zemin_kat_mobilya.dxf` (furniture plan `ZEMİN KAT MOBİLYA PLANI`: walls, openings, furniture, no dimensions), `style_photos/salon_referans.jpg` (not a document) | L0: Salon 19,76 m², Ebeveyn Yatak Odası, Ebeveyn Banyo (en-suite), Mutfak, Hol, Antre, Banyo, Yatak Odası, Çalışma Odası (3+1 flat, notched outline) | furniture plan only (26 pieces incl. two `YATAK_TEK` single beds); Hol, Antre and Çalışma Odası empty | `brief.yaml`: `style` (Modern, white walls), `style_photos: [salon_referans.jpg]`, `polish: false` | none |

Footprints: 01 = 9.6 × 7.2 m, 02 = 8.4 × 6.6 m, 03 = 10.2 × 7.8 m (all levels of a
project share the outline), 04 = 12.0 × 8.0 m, 05 = 13.5 × 9.0 m with a 3.0 × 1.75 m
recess at the bottom right (six outer walls). Outer walls 0.25 m, inner walls 0.10 m,
ceiling 2.70 m assumed (no section: one warning per level).

### What synthetic-04 and synthetic-05 add

| Project | Purpose (what no earlier project covers) | Expected ingest result |
|---|---|---|
| `synthetic-04` | non-rectangular rooms (two L shapes); a single-level vector project on a level other than L-1/L0/L1; the same level as DXF and vector PDF, both with furniture (the PDF footprints carry no type and must match the typed DXF pieces); furniture at a non-right angle; the bathtub block; a combined `SALON + MUTFAK` label (room type `living`, its kitchen pieces stay kitchen pieces); a walnut floor and the Japandi family | status ok, 10 walls (4 exterior), 15 openings (5 doors, 10 windows), 5 rooms, 21 pieces with 2 evidence entries each (DXF `INSERT` + PDF `path`), 0 conflicts, 0 unverified, the 45° armchair (rotation 315°, front 225°) matched across DXF and PDF; 2 rooms for the AI layout (Hol, Çocuk Odası) |
| `synthetic-05` | a notched outline (`LevelBuilder(outline=...)`); the branch "floor plan without furniture + furniture plan = the furniture source" end to end; an en-suite labelled `EBEVEYN BANYO` (room type `bathroom`); two bathrooms on one level; room type `other` (`ÇALIŞMA ODASI`); single beds; a style photo; `polish: false` | status ok, 14 walls (6 exterior, each with evidence from both DXFs), 19 openings (9 doors, 10 windows), 9 rooms, 26 pieces (furniture-plan evidence only), 0 conflicts, 0 unverified, warning `Zemin Kat: furniture taken from zemin_kat_mobilya.dxf (26 pieces); zemin_kat.dxf draws none`; 3 rooms for the AI layout (Hol, Antre, Çalışma Odası); with the photo terms the floor becomes `concrete_polished` (photo), the walls stay white (the brief wins) |

The style photo of synthetic-05 is a byte copy of
`tests/fixtures/style_photo_synthetic-03_salon.jpg` (our own Milestone 4 render of
the synthetic-03 Salon, no third-party image), listed in `Project.style_photos` and
copied by `generate_project`. The ingest reads only the top level of a project
folder (`wenart/ingest/classify.py`), so `style_photos/` is never a document.

Room types come from `wenart.building.room_type_for` (also used for the truth): a
keyword matches at the start of a word (`banyosu` → `banyo`), and when several match
the type earliest in `wc > bathroom > storage > balcony > bedroom > living > kitchen >
hall > other` wins (`EBEVEYN BANYO` → bathroom, `SALON + MUTFAK` → living). The
Milestone 6 keywords `lavabo`/`tuvalet` → wc, `dus` → bathroom, `giris` → hall,
`teras` → balcony, `calisma` → other left the room types of synthetic-01..03
unchanged (`tests/test_building.py` pins every room of the five projects).

All layouts live in `wenart/synthetic/projects.py` as readable code; the room
polygons, IDs, door rotations and furniture-to-room links are derived from the
walls by `wenart/synthetic/model.py` (shapely union of the wall rectangles,
interior rings = rooms). The generator refuses inconsistent layouts (label in
no room, opening off its wall, furniture crossing a wall).

Outer walls: `LevelBuilder(title, width, height)` draws the four walls of the
rectangle (indices 0..3: bottom, right, top, left). `LevelBuilder(title,
outline=[(x, y), ...])` takes the outer face of a non-rectangular building
(axis-aligned edges, bounding box from the origin) and draws one outer wall per
edge, in edge order: each wall runs to the outer corner at a convex vertex and
on to the inner corner (one wall thickness past the vertex) at a reflex vertex,
so the wall rectangles overlap at every corner and their union is one closed
ring. The default rectangle is the same rule with four vertices.

## Coordinate conventions

| Frame | Units | Origin | Axes | Where |
|---|---|---|---|---|
| Building | metres | outer corner of the outer wall of L0 | X right, Y up, rotation CCW in degrees | `truth/building.json`, all `wenart.synthetic.model` data |
| DXF model space | millimetres (`$INSUNITS = 4`) | same as building | same | `*.dxf`; `building_to_page = [1000, 0, 0, 0, 1000, 0]` |
| PDF page | points, A3 landscape 1190.55 × 841.89 | bottom-left | Y up | `*.pdf`; 1 m = 28.3465 pt (1:100); the plan is centred, offset `(x0, y0)` is in the page transform |
| Raster | pixels, 2481 × 1754 at 150 dpi | top-left | Y down | `*_scan.png`, `*_photo.jpg` |

Transforms are stored per page in `truth/pages.json` as
`transform: {kind: "affine" | "homography", building_to_page: [...]}`. An affine
is six numbers `[a, b, c, d, e, f]` meaning `x' = a·x + b·y + c`,
`y' = d·x + e·y + f` (same layout as `transform_to_building` in the schema, which
holds the inverse). A homography is nine numbers row-major. Raster pages also
carry `H_building_to_pixels` as a 3×3 nested list. Helpers:
`wenart.geometry.apply_transform`, `transform_box`, `invert_affine`, `invert_homography`.

Scan = PDF page rasterised with `pdftoppm -r 150 -gray`, rotated by a seeded angle
in ±1.5°, Gaussian noise (σ = 4), slight blur (σ = 0.7). Photo = the scan warped by a
perspective transform (corners moved inward by up to 6 %), grey background outside
the paper, a brightness gradient, JPEG quality 80. Pixel boxes in the truth are the
axis-aligned boxes of the transformed corners; `tests/test_synthetic.py` checks that
every box sits on ink.

## Drawing conventions (what the extractors must read)

- Walls: closed 4-corner `LWPOLYLINE` on layer `DUVAR` (DXF) / closed path with
  line width 0.5 pt (PDF). Long axis = centre line, short side = thickness. Outer
  walls run corner to corner (they overlap at the corners); inner walls run face to
  face. `wenart.geometry.rectangle_to_centerline` does the conversion.
- Openings: block inserts `KAPI_80/90` on `KAPI`, `PENCERE_60/120/180` on `PENCERE`;
  the insert point is the opening centre on the wall centre line, the rotation is the
  wall direction, or the wall direction + 180° when the door swings to the other side.
  Door block: hinge at local (−w/2, 0), leaf line to (−w/2, w), swing arc of radius w
  from 0° to 90° around the hinge, so the door opens towards local +Y. Window block:
  two parallel lines 0.10 m apart plus the two end lines. In the PDF the same geometry
  is drawn with 0.35 pt lines (the door arc is the only curve on a page).
- Furniture: block inserts on `MOBILYA`; block names, types and sizes are in
  `wenart/synthetic/blocks.py: BLOCKS` (the only copy). Block local frame: rectangle
  centred at the origin, `size = [width (X), depth (Y)]`, front = −Y, so
  `front_deg = (270 + rotation) mod 360`. Each block draws its rectangle plus a short
  line parallel to the front edge (inset up to 50 mm). `BLOK_A` (1.2 × 0.5 m) has no known
  type: the truth lists it as `type: unknown`, `status: unverified`.
- Texts on `YAZI`: level title (`ZEMİN KAT PLANI`, `1. KAT PLANI`, `BODRUM KAT PLANI`,
  and `ZEMİN KAT MOBİLYA PLANI` for the furniture plan), `ÖLÇEK 1/100` to the right of
  the title, one room label per room inside the room (left baseline = insertion
  point). DXF text heights: labels 200 mm, title 500 mm, scale 300 mm, dimensions
  200 mm. PDF: 8 pt labels, 10 pt title, 9 pt scale, 8 pt dimensions.
- Dimensions on `OLCU`: a chain along the bottom and the left outer wall (segments
  between wall centre lines) plus the overall length further out. DXF: `DIMENSION`
  entities created with ezdxf's `add_aligned_dim` (stored as linear dimensions
  rotated to the direction of the two definition points, `dimtype` 0; the measurement
  is the distance between `defpoint2` and `defpoint3`), dimstyle `WENART`
  (`dimlfac 0.001`, `dimdec 2`, `dimdsep ","`, `dimzin 0`), `text = "<>"` except the
  deliberate override `3,99`. `wenart.synthetic.dxf_writer.dimension_printed_text`
  returns what a viewer prints. PDF: line, two extension lines, two 45° ticks and the
  text `5,30` (rotated 90° for vertical chains).

## Truth files

`truth/building.json` is schema-valid (`wenart.building.validate`) and holds what the
pipeline should produce. Rules used by the generator:

- Elements get one evidence entry per page that shows them. DXF: `layer` +
  `entity` (`LWPOLYLINE:<handle>`, `INSERT:<handle>`, `TEXT:<handle>`,
  `DIMENSION:<handle>`). PDF: `page` + `entity` (`path:<n>` or `char:<n>`). Rasters:
  `pixel_box` (+ `dpi` for scans) with `method: ai` for geometry/symbols and
  `method: ocr` for texts, confidence 1.0. Rooms get a second entry
  `method: derived`, `entity: derived-from:<wall ids>`.
- IDs follow docs/milestone2.md: `L-1`, `L0`, `L1`; `w_L0_001`; `d_L0_001`;
  `win_L0_001`; `r_L0_salon`, `r_L0_yatak_odasi`, `r_L-1_kiler_2`; `f_L0_001`; `c_001`.
  Room slugs use the whole normalised label (`wenart.building.room_id`).
- Heights, sill heights and furniture heights are `null` (not drawn). Wall `height`
  is the assumed ceiling height. `created_utc` and `pipeline_commit` are constants.
- For synthetic-03's Zemin Kat the DXF is the master: elements present in both
  documents carry both evidence entries; the window missing from the PDF has DXF
  evidence only and conflict `c_003`.

`truth/pages.json`: one entry per drawn page, including the hidden
`truth/plan.pdf` of synthetic-02 (`"hidden": true`; it is not a project document):
`{file, page, class, kind, level_id, level_label_raw, units, size, dpi,
scale_metres_per_unit, transform, H_building_to_pixels (rasters), texts, symbols,
walls, dimensions}`. Boxes are `[x0, y0, x1, y1]` in page units. `texts` carry
`role` (`title`, `scale`, `room_label`, `dimension`) and `symbols` carry `id`,
`type` (furniture type, `door` or `window`), `block`, `rotation_deg` and the entity.

## Known deviations and caveats

- PDF font is DejaVu Sans (embedded, from matplotlib's data folder), not Helvetica:
  reportlab's built-in Helvetica cannot encode `İ`, `Ş`, `Ğ`. Sizes follow the spec.
- `path:<n>` counts path drawing operations in emission order (border = 0, then
  walls, openings, furniture, dimensions). pdfplumber does not expose stream order
  and splits a path into `rects`, `lines` and `curves`, so match PDF elements by
  geometry (every box is in `pages.json`) and treat the index as a label.
  `char:<n>` is verified against `page.chars` order in the tests.
- The photo page has no single scale (`scale: null`, `transform_to_building: null`
  in building.json); use `H_building_to_pixels` from pages.json.
- Scans are ~1.4 MB each (noise does not compress well); the whole set is ~3.8 MB
  (synthetic-04 and -05 together ~0.5 MB, most of it the 78 KB style photo and the DXFs).
- Previews: `results/synthetic/<project>_<file stem>_p<page>.jpg`, ≤ 1200 px wide,
  ≤ 300 KB (13 files for the five projects). The DXF previews are rendered from the
  written file with ezdxf's matplotlib backend. The names derive from the file stem,
  so two documents of one project need different stems: synthetic-04's PDF is
  `3_kat_plani_pdf.pdf` next to `3_kat_plani.dxf`.
- pdfplumber lists a straight-sided closed path that is not an axis-aligned
  rectangle under `curves` too: on synthetic-04's PDF page the 45° armchair is such
  a "curve"; the door arcs are the only paths with Bézier segments.
- Prototype record (2 Oct 2026, session scratch): synthetic-04/05 were prototyped
  end to end on CPU (ingest 0 problems against the truth, fit, decor, the AI-layout
  placer on the L-shaped Hol, a Blender CPU build of synthetic-04). Issues found
  there are fixed in Milestone 6 outside this generator (wall-face materials per
  room span, the windowless-room light position, searched cameras).
