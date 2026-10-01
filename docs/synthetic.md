# Synthetic test projects (Milestone 2, §1)

Three generated projects with known ground truth, used to test the vector path
(`wenart/ingest`) and the raster bake-off (`wenart/recognition`).

```
python -m wenart.synthetic.generate --out projects --results results/synthetic
```

The command is deterministic and idempotent: fixed seeds, fixed DXF/PDF metadata,
byte-identical files on every run (`tests/test_synthetic.py::test_deterministic`
and `test_committed_projects_are_current` check this). After changing the
generator, run it again and commit `projects/` and `results/synthetic/`.

## The three projects

| Project | Documents | Levels / rooms | Furniture in documents | Brief | Deliberate conflicts |
|---|---|---|---|---|---|
| `synthetic-01` | `zemin_kat.dxf` (L0), `1_kat.pdf` (L1, vector), `1_kat_scan.png` (scan of the PDF) | L0: Salon 24,50 m², Mutfak, Yatak Odası, Banyo, Hol; L1: Ebeveyn Yatak Odası, Çocuk Odası, Hol, Yatak Odası, Banyo | L0 only, in Salon, Yatak Odası, Banyo (13 pieces) | `brief.yaml`: one `style` | none (the Salon label matches the polygon exactly) |
| `synthetic-02` | `plan_scan.png` (scan), `plan_photo.jpg` (phone photo). The source vector PDF is hidden in `truth/plan.pdf` | L0: Salon, Mutfak, Antre, Banyo, Yatak Odası (1+1 flat) | all rooms (19 pieces) | none (defaults) | none |
| `synthetic-03` | `kat_planlari.pdf` (3 pages: Bodrum, Zemin, 1. Kat), `mobilya_plani.dxf` (furniture plan of Zemin Kat: walls, openings, furniture, no dimensions) | L-1: Kiler ×2, Hol, Yatak Odası, WC, Banyo; L0: Salon, Mutfak, Antre, Hol, Yatak Odası, WC, Kiler; L1: Ebeveyn Yatak Odası, Çocuk Odası, Hol, Yatak Odası, Banyo, Balkon | L0 only, DXF only (21 pieces incl. one `BLOK_A` of unknown type) | `brief.yaml`: `styles: [two prompts]` | `c_001` Salon label 24,00 m² vs 23,50 m² computed (2 %, within tolerance); `c_002` Bodrum left dimension prints `3,99` for 3,80 m (5 %); `c_003` the PDF Zemin page lacks the Mutfak window that the DXF has (count mismatch, DXF wins) |

Footprints: 01 = 9.6 × 7.2 m, 02 = 8.4 × 6.6 m, 03 = 10.2 × 7.8 m (all levels of a
project share the outline). Outer walls 0.25 m, inner walls 0.10 m, ceiling 2.70 m
assumed (no section: one warning per level).

All layouts live in `wenart/synthetic/projects.py` as readable code; the room
polygons, IDs, door rotations and furniture-to-room links are derived from the
walls by `wenart/synthetic/model.py` (shapely union of the wall rectangles,
interior rings = rooms). The generator refuses inconsistent layouts (label in
no room, opening off its wall, furniture crossing a wall).

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
- Scans are ~1.4 MB each (noise does not compress well); the whole set is ~3.3 MB.
- Previews: `results/synthetic/<project>_<file stem>_p<page>.jpg`, ≤ 1200 px wide,
  ≤ 300 KB. The DXF previews are rendered from the written file with ezdxf's
  matplotlib backend.
